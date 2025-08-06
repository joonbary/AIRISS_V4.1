#!/bin/bash

# AIRISS MSA Backup Script
# 자동 백업 스크립트 (데이터베이스, 설정, 로그)

set -e

# 설정
BACKUP_DIR="/backup"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_PREFIX="airiss_backup_${TIMESTAMP}"
RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-30}

# 색상
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[BACKUP]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# 백업 디렉토리 생성
mkdir -p ${BACKUP_DIR}/${TIMESTAMP}

# 1. PostgreSQL 데이터베이스 백업
backup_database() {
    log_info "데이터베이스 백업 시작..."
    
    if [ -n "$DATABASE_URL" ]; then
        pg_dump $DATABASE_URL > ${BACKUP_DIR}/${TIMESTAMP}/database.sql
        
        # 압축
        gzip ${BACKUP_DIR}/${TIMESTAMP}/database.sql
        
        log_info "데이터베이스 백업 완료: database.sql.gz"
    else
        log_info "데이터베이스 사용 안 함 - 백업 스킵"
    fi
}

# 2. Redis 데이터 백업
backup_redis() {
    log_info "Redis 캐시 백업 시작..."
    
    if [ -n "$REDIS_HOST" ]; then
        redis-cli -h $REDIS_HOST -a $REDIS_PASSWORD --rdb ${BACKUP_DIR}/${TIMESTAMP}/redis.rdb
        
        # 압축
        gzip ${BACKUP_DIR}/${TIMESTAMP}/redis.rdb
        
        log_info "Redis 백업 완료: redis.rdb.gz"
    else
        log_info "Redis 사용 안 함 - 백업 스킵"
    fi
}

# 3. 설정 파일 백업
backup_configs() {
    log_info "설정 파일 백업 시작..."
    
    # 환경 설정
    cp /app/.env ${BACKUP_DIR}/${TIMESTAMP}/.env 2>/dev/null || true
    
    # Docker 설정
    cp /app/docker-compose.*.yml ${BACKUP_DIR}/${TIMESTAMP}/ 2>/dev/null || true
    
    # Nginx 설정
    cp -r /app/nginx ${BACKUP_DIR}/${TIMESTAMP}/ 2>/dev/null || true
    
    # 모니터링 설정
    cp -r /app/monitoring ${BACKUP_DIR}/${TIMESTAMP}/ 2>/dev/null || true
    
    log_info "설정 파일 백업 완료"
}

# 4. 로그 파일 백업
backup_logs() {
    log_info "로그 파일 백업 시작..."
    
    if [ -d "/app/logs" ]; then
        # 최근 7일 로그만 백업
        find /app/logs -type f -mtime -7 -exec cp {} ${BACKUP_DIR}/${TIMESTAMP}/ \;
        
        # 압축
        tar -czf ${BACKUP_DIR}/${TIMESTAMP}/logs.tar.gz -C ${BACKUP_DIR}/${TIMESTAMP} . --exclude='*.tar.gz'
        
        log_info "로그 파일 백업 완료: logs.tar.gz"
    else
        log_info "로그 디렉토리 없음 - 백업 스킵"
    fi
}

# 5. 전체 백업 압축
create_archive() {
    log_info "백업 아카이브 생성 중..."
    
    cd ${BACKUP_DIR}
    tar -czf ${BACKUP_PREFIX}.tar.gz ${TIMESTAMP}/
    
    # 개별 파일 삭제
    rm -rf ${TIMESTAMP}/
    
    log_info "백업 아카이브 생성 완료: ${BACKUP_PREFIX}.tar.gz"
}

# 6. S3 업로드 (선택사항)
upload_to_s3() {
    if [ -n "$BACKUP_S3_BUCKET" ] && command -v aws &> /dev/null; then
        log_info "S3 업로드 시작..."
        
        aws s3 cp ${BACKUP_DIR}/${BACKUP_PREFIX}.tar.gz \
            s3://${BACKUP_S3_BUCKET}/airiss/backups/${BACKUP_PREFIX}.tar.gz
        
        log_info "S3 업로드 완료"
    fi
}

# 7. 오래된 백업 삭제
cleanup_old_backups() {
    log_info "오래된 백업 정리 중..."
    
    # 로컬 백업 정리
    find ${BACKUP_DIR} -name "airiss_backup_*.tar.gz" -mtime +${RETENTION_DAYS} -delete
    
    # S3 백업 정리 (선택사항)
    if [ -n "$BACKUP_S3_BUCKET" ] && command -v aws &> /dev/null; then
        aws s3 ls s3://${BACKUP_S3_BUCKET}/airiss/backups/ | \
        while read -r line; do
            createDate=$(echo $line | awk {'print $1" "$2'})
            createDate=$(date -d "$createDate" +%s)
            olderThan=$(date -d "${RETENTION_DAYS} days ago" +%s)
            if [[ $createDate -lt $olderThan ]]; then
                fileName=$(echo $line | awk {'print $4'})
                if [ ! -z "$fileName" ]; then
                    aws s3 rm s3://${BACKUP_S3_BUCKET}/airiss/backups/$fileName
                    log_info "삭제됨: $fileName"
                fi
            fi
        done
    fi
    
    log_info "백업 정리 완료"
}

# 8. 백업 검증
verify_backup() {
    log_info "백업 검증 중..."
    
    if [ -f "${BACKUP_DIR}/${BACKUP_PREFIX}.tar.gz" ]; then
        tar -tzf ${BACKUP_DIR}/${BACKUP_PREFIX}.tar.gz > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            log_info "백업 검증 성공"
            
            # 백업 크기 확인
            size=$(du -h ${BACKUP_DIR}/${BACKUP_PREFIX}.tar.gz | cut -f1)
            log_info "백업 크기: $size"
        else
            log_error "백업 검증 실패!"
            exit 1
        fi
    else
        log_error "백업 파일이 생성되지 않음!"
        exit 1
    fi
}

# 9. 알림 전송
send_notification() {
    # Slack 알림
    if [ -n "$SLACK_WEBHOOK_URL" ]; then
        curl -X POST $SLACK_WEBHOOK_URL \
            -H 'Content-Type: application/json' \
            -d "{
                \"text\": \"AIRISS 백업 완료\",
                \"attachments\": [{
                    \"color\": \"good\",
                    \"title\": \"백업 정보\",
                    \"fields\": [
                        {\"title\": \"파일명\", \"value\": \"${BACKUP_PREFIX}.tar.gz\", \"short\": true},
                        {\"title\": \"크기\", \"value\": \"$size\", \"short\": true},
                        {\"title\": \"시간\", \"value\": \"$(date)\", \"short\": false}
                    ]
                }]
            }"
    fi
    
    # 이메일 알림 (sendmail 필요)
    if [ -n "$ALERT_EMAIL" ] && command -v sendmail &> /dev/null; then
        echo "Subject: AIRISS 백업 완료
        
백업이 성공적으로 완료되었습니다.
파일명: ${BACKUP_PREFIX}.tar.gz
크기: $size
시간: $(date)" | sendmail $ALERT_EMAIL
    fi
}

# 메인 백업 프로세스
main() {
    log_info "======================================"
    log_info "AIRISS MSA 백업 시작"
    log_info "======================================"
    
    # 백업 실행
    backup_database
    backup_redis
    backup_configs
    backup_logs
    create_archive
    upload_to_s3
    cleanup_old_backups
    verify_backup
    send_notification
    
    log_info "======================================"
    log_info "백업 완료: ${BACKUP_PREFIX}.tar.gz"
    log_info "======================================"
}

# 스크립트 실행
main