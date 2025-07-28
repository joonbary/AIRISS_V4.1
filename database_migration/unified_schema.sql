-- AIRISS v4 통합 스키마 설계
-- 목표: results와 analysis_results 테이블을 통합한 단일 스키마

-- 1. 통합 analysis_results 테이블 (신규 설계)
CREATE TABLE IF NOT EXISTS analysis_results_v2 (
    -- Primary Key
    id SERIAL PRIMARY KEY,
    
    -- Unique Identifiers
    analysis_id VARCHAR(36) UNIQUE NOT NULL,
    job_id VARCHAR(36) NOT NULL,  -- results 테이블과의 호환성
    
    -- Employee & File Info
    uid VARCHAR(100) NOT NULL,
    file_id VARCHAR(100),
    filename VARCHAR(500),
    
    -- Original Data
    opinion TEXT,
    
    -- Core Scores (통합)
    overall_score REAL,  -- results의 overall_score = analysis_results의 hybrid_score
    text_score REAL,
    quantitative_score REAL,
    confidence REAL,
    
    -- Grade Information
    ok_grade VARCHAR(10),
    grade_description TEXT,
    percentile REAL,  -- results 테이블에서 가져옴
    
    -- Detailed Analysis
    dimension_scores JSONB,  -- PostgreSQL에서는 JSONB, SQLite에서는 JSON
    
    -- AI Analysis Results (신규 기능)
    ai_feedback JSONB,
    ai_strengths TEXT,
    ai_weaknesses TEXT,
    ai_recommendations JSONB,
    ai_error TEXT,  -- AI 처리 오류 메시지
    
    -- Full Result Data (원본 보존)
    result_data JSONB,  -- 전체 분석 결과 JSON
    
    -- Metadata
    analysis_mode VARCHAR(20) DEFAULT 'hybrid',
    version VARCHAR(10) DEFAULT '4.0',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_job_id (job_id),
    INDEX idx_uid (uid),
    INDEX idx_file_id (file_id),
    INDEX idx_created_at (created_at),
    INDEX idx_overall_score (overall_score)
);

-- 2. 트리거: updated_at 자동 업데이트 (PostgreSQL)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_analysis_results_v2_updated_at 
    BEFORE UPDATE ON analysis_results_v2
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- 3. 뷰: 기존 API 호환성을 위한 results 뷰
CREATE OR REPLACE VIEW results_view AS
SELECT 
    CAST(id AS TEXT) as id,
    job_id,
    uid,
    overall_score,
    ok_grade as grade,
    percentile,
    text_score,
    quantitative_score,
    confidence,
    dimension_scores::TEXT as dimension_scores,
    result_data::TEXT as result_data,
    created_at
FROM analysis_results_v2;

-- 4. 뷰: 기존 analysis_results 호환 뷰
CREATE OR REPLACE VIEW analysis_results_view AS
SELECT 
    id,
    analysis_id,
    uid,
    file_id,
    filename,
    opinion,
    overall_score as hybrid_score,  -- 매핑
    text_score,
    quantitative_score,
    ok_grade,
    grade_description,
    confidence,
    dimension_scores,
    ai_feedback,
    ai_strengths,
    ai_weaknesses,
    ai_recommendations,
    analysis_mode,
    version,
    created_at,
    updated_at
FROM analysis_results_v2;

-- 5. 인덱스 추가 (성능 최적화)
CREATE INDEX IF NOT EXISTS idx_analysis_results_v2_composite 
    ON analysis_results_v2(job_id, uid);

CREATE INDEX IF NOT EXISTS idx_analysis_results_v2_scores 
    ON analysis_results_v2(overall_score DESC, created_at DESC);

-- 6. 통계 테이블 (선택사항)
CREATE TABLE IF NOT EXISTS analysis_statistics (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    total_analyses INTEGER DEFAULT 0,
    average_score REAL,
    top_score REAL,
    bottom_score REAL,
    ai_analyses_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date)
);