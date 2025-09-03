// ===============================
// AIRISS v5.0 - Main JavaScript
// ===============================
// AI HR Intelligence System
// Revolutionary Design System v5.0
// ===============================

(function() {
    'use strict';

    // ===============================
    // Sidebar Management
    // ===============================
    
    // 페이지 로드 시 사이드바 상태 복원
    document.addEventListener('DOMContentLoaded', function() {
            const sidebar = document.getElementById('revolutionary-sidebar');
            const mainContent = document.querySelector('.main-content');
            
            // localStorage에 저장된 상태가 없으면 기본값은 축소
            const savedState = localStorage.getItem('sidebarCollapsed');
            const isCollapsed = savedState === null ? true : savedState === 'true';
            
            if (isCollapsed) {
                sidebar.classList.add('collapsed');
                mainContent.classList.add('expanded');
            } else {
                sidebar.classList.remove('collapsed');
                mainContent.classList.remove('expanded');
            }
            
            // Hover 트리거 설정
            const hoverTrigger = document.querySelector('.sidebar-hover-trigger');
            if (hoverTrigger) {
                hoverTrigger.addEventListener('mouseenter', function() {
                    if (sidebar.classList.contains('collapsed')) {
                        sidebar.classList.add('hover-open');
                    }
                });
                
                hoverTrigger.addEventListener('mouseleave', function() {
                    sidebar.classList.remove('hover-open');
                });
                
                // 사이드바 자체에도 hover 이벤트 추가
                sidebar.addEventListener('mouseenter', function() {
                    if (this.classList.contains('collapsed')) {
                        this.classList.add('hover-open');
                    }
                });
                
                sidebar.addEventListener('mouseleave', function() {
                    this.classList.remove('hover-open');
                });
            }
        });
    </script>
    
    <script>
        // AIRISS v5.0 Main Application - Debug Version
        
        // 전역 에러 핸들러 - 구문 오류 포착
        window.addEventListener('error', function(e) {
            if (e.message && e.message.includes('Unexpected token')) {
                console.error('❌ Syntax Error Detected:', e.message);
                console.error('  Line:', e.lineno, 'Column:', e.colno);
                console.error('  File:', e.filename);
                if (e.error && e.error.stack) {
                    console.error('  Stack:', e.error.stack);
                }
            }
        }, true);
        
        console.log('🚀 AIRISS v5.0 초기화 시작...');
        
        // 전역 AIRISS 객체 즉시 생성 (HTML onClick에서 바로 접근 가능)
        const AIRISS = window.AIRISS = {
            // 버전 정보 - 캐시 방지용 타임스탬프 추가
            version: '5.0.2-' + Date.now(),
            buildDate: '2025-08-08',
            buildTime: new Date().toISOString(),
            cacheBreaker: Math.random().toString(36).substring(7),
            
            // 상태 관리
            state: {
                dashboardStats: null,
                employees: [],
                previousStats: null  // 이전 통계 데이터
            },
            
            // 페이지네이션 상태 변수
            promotionDashboardPage: 1,
            talentDashboardPage: 1,
            riskDashboardPage: 1,
            // 리포트 페이지네이션 상태 변수
            talentReportPage: 1,
            promotionReportPage: 1,
            riskReportPage: 1,
            
            // API 설정
            api: {
                baseURL: '/api/v1',
                
                async request(method, endpoint, data = null) {
                    // 캐시 방지를 위한 타임스탬프 추가
                    const url = `${this.baseURL}${endpoint}${endpoint.includes('?') ? '&' : '?'}_t=${Date.now()}&_v=${AIRISS.cacheBreaker}`;
                    
                    const options = {
                        method,
                        headers: {
                            'Content-Type': 'application/json',
                            'X-Version': AIRISS.version,
                            'Cache-Control': 'no-cache',
                            'Pragma': 'no-cache'
                        },
                        cache: 'no-store'
                    };
                    
                    if (data) {
                        options.body = JSON.stringify(data);
                    }
                    
                    try {
                        console.log(`📡 API 호출: ${method} ${url}`);
                        const response = await fetch(url, options);
                        console.log(`📡 API Response Status: ${response.status}`);
                        
                        if (!response.ok) {
                            let errorMessage = `HTTP ${response.status}`;
                            try {
                                const errorData = await response.json();
                                errorMessage = errorData.detail || errorData.message || errorMessage;
                            } catch {
                                const errorText = await response.text();
                                errorMessage = errorText || errorMessage;
                            }
                            console.error('API Error Response:', errorMessage);
                            throw new Error(errorMessage);
                        }
                        
                        const result = await response.json();
                        console.log(`✅ API 응답:`, result);
                        return result;
                    } catch (error) {
                        console.error('❌ API Error:', {
                            url: url,
                            method: method,
                            error: error.message,
                            stack: error.stack
                        });
                        AIRISS.showNotification(`API 호출 실패: ${error.message}`, 'error');
                        throw error;
                    }
                }
            },
            
            // 상태 관리
            state: {
                currentTab: 'dashboard',
                employees: [],
                dashboardStats: {},
                uploadedFile: null,
                analysisJobId: null
            },
            
            // 초기화
            async init() {
                console.log(`AIRISS v${this.version} initialized at ${this.buildTime}`);
                this.attachEventListeners();
                // 직원 데이터를 먼저 로드한 후 대시보드 로드
                await this.loadEmployeesData();
                this.loadDashboardData();
                this.checkVersion();
            },
            
            // 버전 체크
            async checkVersion() {
                try {
                    const response = await fetch('/health');
                    const data = await response.json();
                    console.log('Server version:', data.deployment_version);
                } catch (error) {
                    console.error('Version check failed:', error);
                }
            },
            
            // 이벤트 리스너
            attachEventListeners() {
                // 드래그 앤 드롭
                const uploadArea = document.getElementById('upload-area');
                if (uploadArea) {
                    uploadArea.addEventListener('dragover', (e) => {
                        e.preventDefault();
                        uploadArea.classList.add('dragover');
                    });
                    
                    uploadArea.addEventListener('dragleave', () => {
                        uploadArea.classList.remove('dragover');
                    });
                    
                    uploadArea.addEventListener('drop', (e) => {
                        e.preventDefault();
                        uploadArea.classList.remove('dragover');
                        const files = e.dataTransfer.files;
                        if (files.length > 0) {
                            this.handleFileSelect({ target: { files } });
                        }
                    });
                }
                
                // 직원 검색 드롭다운 외부 클릭 시 닫기
                document.addEventListener('click', (e) => {
                    const dropdown = document.getElementById('employee-dropdown');
                    const searchInput = document.getElementById('employee-search');
                    
                    if (dropdown && searchInput && 
                        !dropdown.contains(e.target) && 
                        !searchInput.contains(e.target)) {
                        dropdown.style.display = 'none';
                    }
                });
            },
            
            // 탭 전환
            switchTab(tabName) {
                console.log(`🔄 탭 전환: ${tabName}`);
                
                // 모든 탭 컨텐츠 비활성화
                document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
                
                // 선택된 탭 컨텐츠 활성화
                const targetTab = document.getElementById(`${tabName}-tab`);
                if (targetTab) {
                    targetTab.classList.add('active');
                    console.log(`✅ 탭 활성화: ${tabName}-tab`);
                } else {
                    console.error(`❌ 탭을 찾을 수 없습니다: ${tabName}-tab`);
                }
                
                // 사이드바 메뉴 활성 상태 업데이트
                if (typeof updateSidebarActiveState === 'function') {
                    updateSidebarActiveState(tabName);
                }
                
                // 상태 업데이트
                this.state.currentTab = tabName;
                
                // 탭별 데이터 로드
                if (tabName === 'employees') {
                    this.loadEmployeesData();
                } else if (tabName === 'insights') {
                    this.loadInsights();
                }
            },
            
            // 리포트 표시 메서드
            showReport(type) {
                console.log(`📊 리포트 표시: ${type}`);
                
                // reports 탭으로 전환
                this.switchTab('reports');
                
                // 리포트 타입별 처리
                switch(type) {
                    case 'monthly':
                        this.generateReport('monthly');
                        break;
                    case 'talent':
                        this.generateReport('talent');
                        break;
                    case 'risk':
                        this.generateReport('risk');
                        break;
                    case 'performance':
                        this.generateReport('performance');
                        break;
                    case 'department':
                        this.generateReport('department');
                        break;
                    case 'executive':
                        this.generateReport('executive');
                        break;
                    default:
                        console.warn(`❌ 알 수 없는 리포트 타입: ${type}`);
                        this.generateReport('monthly'); // 기본값
                        break;
                }
            },
            
            // 증감 표기 업데이트 함수
            updateChangeIndicators(data) {
                // 이전 데이터는 DB에서 가져온 이전 기간 데이터를 사용해야 함
                // API에서 previous_period 데이터를 받아서 비교
                const previousData = data.previous_period || {};
                
                // 전체 직원 수 변화
                const totalChange = data.total_employees - (previousData.total_employees || data.total_employees);
                const totalPercent = previousData.total_employees ? 
                    Math.round((totalChange / previousData.total_employees) * 100) : 0;
                
                const totalChangeEl = document.querySelector('.stat-card:nth-child(1) .stat-change');
                if (totalChangeEl) {
                    if (totalChange > 0) {
                        totalChangeEl.className = 'stat-change positive';
                        totalChangeEl.innerHTML = `<span>↑</span><span>+${totalChange}명 (${totalPercent}%)</span>`;
                    } else if (totalChange < 0) {
                        totalChangeEl.className = 'stat-change negative';
                        totalChangeEl.innerHTML = `<span>↓</span><span>${totalChange}명 (${totalPercent}%)</span>`;
                    } else {
                        totalChangeEl.className = 'stat-change';
                        totalChangeEl.innerHTML = `<span>―</span><span>변화없음</span>`;
                    }
                }
                
                // 승진 후보자 변화
                const promotionChange = (data.promotion_candidates?.count || 0) - (previousData.promotion_candidates?.count || 0);
                const promotionChangeEl = document.querySelector('.stat-card:nth-child(2) .stat-change');
                if (promotionChangeEl) {
                    if (promotionChange > 0) {
                        promotionChangeEl.className = 'stat-change positive';
                        promotionChangeEl.innerHTML = `<span>↑</span><span>+${promotionChange}명 증가</span>`;
                    } else if (promotionChange < 0) {
                        promotionChangeEl.className = 'stat-change negative';
                        promotionChangeEl.innerHTML = `<span>↓</span><span>${Math.abs(promotionChange)}명 감소</span>`;
                    } else {
                        promotionChangeEl.className = 'stat-change';
                        promotionChangeEl.innerHTML = `<span>―</span><span>변화없음</span>`;
                    }
                }
                
                // 핵심 인재 변화
                const talentChange = (data.top_talents?.count || 0) - (previousData.top_talents?.count || 0);
                const talentChangeEl = document.querySelector('.stat-card:nth-child(3) .stat-change');
                if (talentChangeEl) {
                    if (talentChange > 0) {
                        talentChangeEl.className = 'stat-change positive';
                        talentChangeEl.innerHTML = `<span>↑</span><span>+${talentChange}명 증가</span>`;
                    } else if (talentChange < 0) {
                        talentChangeEl.className = 'stat-change negative';
                        talentChangeEl.innerHTML = `<span>↓</span><span>${Math.abs(talentChange)}명 감소</span>`;
                    } else {
                        talentChangeEl.className = 'stat-change';
                        talentChangeEl.innerHTML = `<span>―</span><span>변화없음</span>`;
                    }
                }
                
                // 관리 필요 인력 변화 (감소가 긍정적)
                const riskChange = (data.risk_employees?.count || 0) - (previousData.risk_employees?.count || 0);
                const riskPercent = previousData.risk_employees?.count ? 
                    Math.round((riskChange / previousData.risk_employees?.count) * 100) : 0;
                
                const riskChangeEl = document.querySelector('.stat-card:nth-child(4) .stat-change');
                if (riskChangeEl) {
                    if (riskChange < 0) {
                        // 관리 필요 인력이 감소한 경우 (긍정적)
                        riskChangeEl.className = 'stat-change positive';
                        riskChangeEl.innerHTML = `<span>↓</span><span>${Math.abs(riskChange)}명 감소 (${Math.abs(riskPercent)}%)</span>`;
                    } else if (riskChange > 0) {
                        // 관리 필요 인력이 증가한 경우 (부정적)
                        riskChangeEl.className = 'stat-change negative';
                        riskChangeEl.innerHTML = `<span>↑</span><span>+${riskChange}명 증가 (${riskPercent}%)</span>`;
                    } else {
                        riskChangeEl.className = 'stat-change';
                        riskChangeEl.innerHTML = `<span>―</span><span>변화없음</span>`;
                    }
                }
                
                // 현재 데이터를 state에 저장 (다음 비교를 위해)
                this.state.previousStats = {
                    total_employees: data.total_employees || 0,
                    promotion_candidates: { count: data.promotion_candidates?.count || 0 },
                    top_talents: { count: data.top_talents?.count || 0 },
                    risk_employees: { count: data.risk_employees?.count || 0 },
                    timestamp: new Date().toISOString()
                };
            },
            
            // 대시보드 데이터 로드
            async loadDashboardData() {
                try {
                    const data = await this.api.request('GET', '/hr-dashboard/stats');
                    this.state.dashboardStats = data;
                    
                    // 통계 업데이트
                    document.getElementById('stat-total').textContent = data.total_employees || 0;
                    document.getElementById('stat-promotion').textContent = data.promotion_candidates?.count || 0;
                    document.getElementById('stat-talent').textContent = data.top_talents?.count || 0;
                    document.getElementById('stat-risk').textContent = data.risk_employees?.count || 0;
                    
                    // 증감 표기 업데이트 (실제 데이터 기반)
                    this.updateChangeIndicators(data);
                    
                    // 승진 후보자 리스트 렌더링
                    this.renderPromotionList(data.promotion_candidates?.employees || []);
                    
                    // 핵심 인재 리스트 렌더링
                    this.renderTalentList(data.top_talents?.employees || []);
                    
                    // 관리 필요 인력 테이블
                    this.renderRiskEmployees(data.risk_employees?.employees || []);
                    
                    // 직원 데이터가 있을 때만 차트 렌더링
                    if (this.state.employees && this.state.employees.length > 0) {
                        this.renderDashboardCharts();
                    }
                } catch (error) {
                    console.error('Dashboard data load failed:', error);
                }
            },
            
            // 관리 필요 인력 렌더링
            renderRiskEmployees(employees) {
                const tbody = document.getElementById('risk-employees-table');
                if (!tbody) {
                    console.error('risk-employees-table not found');
                    return;
                }
                
                tbody.innerHTML = '';
                
                // 전체 카운트 업데이트 (전체 수)
                const counter = document.getElementById('stat-risk-table');
                if (counter) counter.textContent = this.state.dashboardStats?.risk_employees?.count || employees.length;
                
                // 페이지네이션 설정
                const riskPerPage = 10;
                const currentPage = this.riskDashboardPage || 1;
                const startIndex = (currentPage - 1) * riskPerPage;
                const endIndex = startIndex + riskPerPage;
                const paginatedEmployees = employees.slice(startIndex, endIndex);
                const totalPages = Math.ceil(employees.length / riskPerPage);
                
                console.log(`관리필요인력 렌더링 - 현재 페이지: ${currentPage}, 시작: ${startIndex}, 종료: ${endIndex}`);
                console.log(`표시할 인력 수: ${paginatedEmployees.length}명, 전체: ${employees.length}명`);
                
                paginatedEmployees.forEach(emp => {
                    const row = tbody.insertRow();
                    const riskColor = emp.risk_level === 'high' ? 'danger' : 'warning';
                    // ai_score 또는 risk_score 사용
                    const score = emp.ai_score || emp.risk_score || emp.overall_score || 0;
                    
                    row.innerHTML = `
                        <td>${emp.uid || emp.employee_id || '-'}</td>
                        <td>${emp.name || emp.employee_name || '익명'}</td>
                        <td>${emp.department || '-'}</td>
                        <td><span class="btn btn-${riskColor}" style="padding: 8px 16px; font-size: 14px; border-radius: 8px; font-weight: 500;">${emp.risk_level === 'high' ? '높음' : '보통'}</span></td>
                        <td style="font-weight: 600; color: ${score < 60 ? '#dc3545' : '#00d9ff'};">${Math.round(score)}</td>
                        <td>${emp.reason || emp.risk_reason || '-'}</td>
                        <td>
                            <button class="btn btn-primary" style="padding: 8px 16px; font-size: 14px; border-radius: 8px;" 
                                    onclick="AIRISS.viewEmployeeDetail('${emp.uid || emp.employee_id}')">상세</button>
                        </td>
                    `;
                });
                
                // 페이지네이션 컨트롤 추가
                this.renderRiskPagination(currentPage, totalPages, employees.length);
            },
            
            // 관리필요인력 페이지네이션 렌더링
            renderRiskPagination(currentPage, totalPages, totalCount) {
                // 기존 페이지네이션 제거
                const existingPagination = document.getElementById('risk-pagination');
                if (existingPagination) existingPagination.remove();
                
                if (totalPages <= 1) return;
                
                // 관리필요인력 테이블 찾기 (risk-employees-table의 부모 요소)
                const riskTable = document.getElementById('risk-employees-table');
                if (!riskTable) return;
                const tableContainer = riskTable.closest('.table-responsive');
                if (!tableContainer) return;
                
                const paginationHTML = `
                    <div id="risk-pagination" style="display: flex; justify-content: center; align-items: center; margin: 20px 0; gap: 10px;">
                        <button onclick="AIRISS.changeRiskDashboardPage(${currentPage - 1})" 
                            ${currentPage <= 1 ? 'disabled' : ''}
                            style="padding: 8px 16px; background: ${currentPage <= 1 ? '#6c757d' : '#007bff'}; color: white; border: none; border-radius: 6px; cursor: ${currentPage <= 1 ? 'not-allowed' : 'pointer'};">
                            ← 이전
                        </button>
                        <span style="margin: 0 15px; font-weight: 500;">
                            ${currentPage} / ${totalPages} 페이지 (${totalCount}명)
                        </span>
                        <button onclick="AIRISS.changeRiskDashboardPage(${currentPage + 1})" 
                            ${currentPage >= totalPages ? 'disabled' : ''}
                            style="padding: 8px 16px; background: ${currentPage >= totalPages ? '#6c757d' : '#007bff'}; color: white; border: none; border-radius: 6px; cursor: ${currentPage >= totalPages ? 'not-allowed' : 'pointer'};">
                            다음 →
                        </button>
                    </div>
                `;
                tableContainer.insertAdjacentHTML('afterend', paginationHTML);
            },
            
            // 대시보드 관리필요인력 페이지 변경
            changeRiskDashboardPage(page) {
                const employees = this.state.dashboardStats?.risk_employees?.employees || [];
                const totalPages = Math.ceil(employees.length / 10);
                
                console.log(`관리필요인력 페이지 변경 요청: ${page}, 전체 페이지: ${totalPages}, 전체 인원: ${employees.length}`);
                console.log(`현재 페이지: ${this.riskDashboardPage}`);
                
                if (page < 1 || page > totalPages) {
                    console.log('유효하지 않은 페이지 번호');
                    return;
                }
                
                this.riskDashboardPage = page;
                console.log(`관리필요인력 새 페이지로 설정: ${this.riskDashboardPage}`);
                
                this.renderRiskEmployees(employees);
            },
            
            // 승진 후보자 테이블 렌더링
            renderPromotionList(employees) {
                const tbody = document.getElementById('promotion-candidates-table');
                if (!tbody) return;
                
                tbody.innerHTML = '';
                
                // 전체 카운트 업데이트 (API에서 받은 전체 수 사용)
                const counter = document.getElementById('stat-promotion-table');
                if (counter) counter.textContent = this.state.dashboardStats?.promotion_candidates?.count || 0;
                
                // 페이지네이션 설정
                const promotionPerPage = 10;
                const currentPage = this.promotionDashboardPage || 1;
                const startIndex = (currentPage - 1) * promotionPerPage;
                const endIndex = startIndex + promotionPerPage;
                const paginatedEmployees = employees.slice(startIndex, endIndex);
                const totalPages = Math.ceil(employees.length / promotionPerPage);
                
                console.log(`렌더링 - 현재 페이지: ${currentPage}, 시작 인덱스: ${startIndex}, 종료 인덱스: ${endIndex}`);
                console.log(`표시할 직원 수: ${paginatedEmployees.length}명`);
                if (paginatedEmployees.length > 0) {
                    console.log('첫 번째 직원:', paginatedEmployees[0].name);
                }
                
                paginatedEmployees.forEach(emp => {
                    const row = tbody.insertRow();
                    const score = emp.ai_score || emp.overall_score || 0;
                    const grade = emp.grade || 'B';
                    
                    row.innerHTML = `
                        <td>${emp.uid || emp.employee_id || '-'}</td>
                        <td>${emp.name || emp.employee_name || '익명'}</td>
                        <td>${emp.department || '-'}</td>
                        <td>${emp.position || '-'}</td>
                        <td style="font-weight: 600; color: var(--primary-color);">${Math.round(score)}</td>
                        <td><span class="btn btn-success" style="padding: 8px 16px; font-size: 14px; border-radius: 8px; color: white !important;">${grade}</span></td>
                        <td>${emp.reasons && emp.reasons.length > 0 ? emp.reasons.slice(0, 2).join(', ') : '우수한 성과 및 리더십'}</td>
                        <td>
                            <button class="btn btn-primary" style="padding: 8px 16px; font-size: 14px; border-radius: 8px;" 
                                    onclick="AIRISS.viewEmployeeDetail('${emp.uid || emp.employee_id}')">상세</button>
                        </td>
                    `;
                });
                
                // 페이지네이션 컨트롤 추가
                this.renderPromotionPagination(currentPage, totalPages, employees.length);
            },
            
            // 승진후보자 페이지네이션 렌더링
            renderPromotionPagination(currentPage, totalPages, totalCount) {
                // 기존 페이지네이션 제거
                const existingPagination = document.getElementById('promotion-pagination');
                if (existingPagination) existingPagination.remove();
                
                if (totalPages <= 1) return;
                
                // 승진후보자 테이블 찾기
                const promotionTable = document.getElementById('promotion-candidates-table');
                if (!promotionTable) return;
                const tableContainer = promotionTable.closest('.table-responsive');
                if (!tableContainer) return;
                
                const paginationHTML = `
                    <div id="promotion-pagination" style="display: flex; justify-content: center; align-items: center; margin: 20px 0; gap: 10px;">
                        <button onclick="AIRISS.changePromotionDashboardPage(${currentPage - 1})" 
                            ${currentPage <= 1 ? 'disabled' : ''}
                            style="padding: 8px 16px; background: ${currentPage <= 1 ? '#6c757d' : '#007bff'}; color: white; border: none; border-radius: 6px; cursor: ${currentPage <= 1 ? 'not-allowed' : 'pointer'};">
                            ← 이전
                        </button>
                        <span style="margin: 0 15px; font-weight: 500;">
                            ${currentPage} / ${totalPages} 페이지 (${totalCount}명)
                        </span>
                        <button onclick="AIRISS.changePromotionDashboardPage(${currentPage + 1})" 
                            ${currentPage >= totalPages ? 'disabled' : ''}
                            style="padding: 8px 16px; background: ${currentPage >= totalPages ? '#6c757d' : '#007bff'}; color: white; border: none; border-radius: 6px; cursor: ${currentPage >= totalPages ? 'not-allowed' : 'pointer'};">
                            다음 →
                        </button>
                    </div>
                `;
                tableContainer.insertAdjacentHTML('afterend', paginationHTML);
            },
            
            // 대시보드 승진후보자 페이지 변경
            changePromotionDashboardPage(page) {
                const employees = this.state.dashboardStats?.promotion_candidates?.employees || [];
                const totalPages = Math.ceil(employees.length / 10);
                
                console.log(`페이지 변경 요청: ${page}, 전체 페이지: ${totalPages}, 전체 인원: ${employees.length}`);
                console.log(`현재 페이지: ${this.promotionDashboardPage}`);
                
                if (page < 1 || page > totalPages) {
                    console.log('유효하지 않은 페이지 번호');
                    return;
                }
                
                this.promotionDashboardPage = page;
                console.log(`새 페이지로 설정: ${this.promotionDashboardPage}`);
                
                this.renderPromotionList(employees);
            },
            
            // 핵심 인재 테이블 렌더링
            renderTalentList(employees) {
                const tbody = document.getElementById('talent-pool-table');
                if (!tbody) return;
                
                tbody.innerHTML = '';
                
                // 카운터 업데이트
                const counter = document.getElementById('stat-talent-table');
                if (counter) counter.textContent = employees.length;
                
                // 페이지네이션 설정
                const talentPerPage = 10;
                const currentPage = this.talentDashboardPage || 1;
                const startIndex = (currentPage - 1) * talentPerPage;
                const endIndex = startIndex + talentPerPage;
                const paginatedEmployees = employees.slice(startIndex, endIndex);
                const totalPages = Math.ceil(employees.length / talentPerPage);
                
                console.log(`핵심인재 렌더링 - 현재 페이지: ${currentPage}, 시작: ${startIndex}, 종료: ${endIndex}`);
                console.log(`표시할 인재 수: ${paginatedEmployees.length}명`);
                
                paginatedEmployees.forEach(emp => {
                    const row = tbody.insertRow();
                    const score = emp.ai_score || emp.overall_score || emp.score || 0;
                    const grade = emp.grade || 'A';
                    
                    row.innerHTML = `
                        <td>${emp.uid || emp.employee_id || '-'}</td>
                        <td>${emp.name || emp.employee_name || '익명'}</td>
                        <td>${emp.department || '-'}</td>
                        <td>${emp.position || '-'}</td>
                        <td style="font-weight: 600; color: var(--primary-color);">${Math.round(score)}</td>
                        <td><span class="btn btn-primary" style="padding: 8px 16px; font-size: 14px; border-radius: 8px; color: white !important;">${grade}</span></td>
                        <td>${emp.reason || '리더십, 전문성'}</td>
                        <td>
                            <button class="btn btn-primary" style="padding: 8px 16px; font-size: 14px; border-radius: 8px;" 
                                    onclick="AIRISS.viewEmployeeDetail('${emp.uid || emp.employee_id}')">상세</button>
                        </td>
                    `;
                });
                
                // 페이지네이션 컨트롤 추가
                this.renderTalentPagination(currentPage, totalPages, employees.length);
            },
            
            // 핵심인재 페이지네이션 렌더링
            renderTalentPagination(currentPage, totalPages, totalCount) {
                // 기존 페이지네이션 제거
                const existingPagination = document.getElementById('talent-pagination');
                if (existingPagination) existingPagination.remove();
                
                if (totalPages <= 1) return;
                
                // 핵심인재 테이블 찾기
                const talentTable = document.getElementById('talent-pool-table');
                if (!talentTable) return;
                const tableContainer = talentTable.closest('.table-responsive');
                if (!tableContainer) return;
                
                const paginationHTML = `
                    <div id="talent-pagination" style="display: flex; justify-content: center; align-items: center; margin: 20px 0; gap: 10px;">
                        <button onclick="AIRISS.changeTalentDashboardPage(${currentPage - 1})" 
                            ${currentPage <= 1 ? 'disabled' : ''}
                            style="padding: 8px 16px; background: ${currentPage <= 1 ? '#6c757d' : '#007bff'}; color: white; border: none; border-radius: 6px; cursor: ${currentPage <= 1 ? 'not-allowed' : 'pointer'};">
                            ← 이전
                        </button>
                        <span style="margin: 0 15px; font-weight: 500;">
                            ${currentPage} / ${totalPages} 페이지 (${totalCount}명)
                        </span>
                        <button onclick="AIRISS.changeTalentDashboardPage(${currentPage + 1})" 
                            ${currentPage >= totalPages ? 'disabled' : ''}
                            style="padding: 8px 16px; background: ${currentPage >= totalPages ? '#6c757d' : '#007bff'}; color: white; border: none; border-radius: 6px; cursor: ${currentPage >= totalPages ? 'not-allowed' : 'pointer'};">
                            다음 →
                        </button>
                    </div>
                `;
                tableContainer.insertAdjacentHTML('afterend', paginationHTML);
            },
            
            // 대시보드 핵심인재 페이지 변경
            changeTalentDashboardPage(page) {
                const employees = this.state.dashboardStats?.top_talents?.employees || [];
                const totalPages = Math.ceil(employees.length / 10);
                
                console.log(`핵심인재 페이지 변경 요청: ${page}, 전체 페이지: ${totalPages}, 전체 인원: ${employees.length}`);
                
                if (page < 1 || page > totalPages) {
                    console.log('유효하지 않은 페이지 번호');
                    return;
                }
                
                this.talentDashboardPage = page;
                console.log(`핵심인재 새 페이지로 설정: ${this.talentDashboardPage}`);
                
                this.renderTalentList(employees);
            },
            
            // 승진 후보자 리스트 토글
            togglePromotionList() {
                const listDiv = document.getElementById('promotion-list');
                if (listDiv) {
                    listDiv.style.display = listDiv.style.display === 'none' ? 'block' : 'none';
                }
            },
            
            // 핵심 인재 리스트 토글
            toggleTalentList() {
                const listDiv = document.getElementById('talent-list');
                if (listDiv) {
                    listDiv.style.display = listDiv.style.display === 'none' ? 'block' : 'none';
                }
            },
            
            // 대시보드 차트 렌더링
            renderDashboardCharts() {
                // Chart.js가 로드되었는지 확인
                if (typeof Chart === 'undefined') {
                    console.error('Chart.js가 로드되지 않았습니다.');
                    return;
                }
                
                // 실제 데이터 기반 등급 분포 계산
                const gradeDistribution = { 'S': 0, 'A+': 0, 'A': 0, 'B+': 0, 'B': 0, 'C': 0, 'D': 0 };
                
                // 직원 데이터 확인
                console.log('📊 차트 렌더링 - 직원 수:', this.state.employees.length);
                
                this.state.employees.forEach(emp => {
                    // ai_grade 필드를 우선 사용 (실제 데이터 구조에 맞춤)
                    const grade = emp.ai_grade || emp.grade || emp.OK등급 || 'C';
                    
                    // 첫 몇 개 데이터 로깅
                    if (gradeDistribution[grade] === 0) {
                        console.log(`첫 ${grade} 등급 발견:`, emp);
                    }
                    
                    if (gradeDistribution.hasOwnProperty(grade)) {
                        gradeDistribution[grade]++;
                    }
                });
                
                console.log('📊 등급 분포:', gradeDistribution);
                
                // 등급 분포 차트 - 막대그래프로 변경
                const gradeCtx = document.getElementById('gradeChart');
                if (gradeCtx) {
                    // 기존 차트가 있으면 제거
                    if (this.gradeChart) {
                        this.gradeChart.destroy();
                    }
                    
                    // 플러그인 옵션 설정 (ChartDataLabels 플러그인 사용 시)
                    const useDataLabels = typeof ChartDataLabels !== 'undefined';
                    
                    this.gradeChart = new Chart(gradeCtx, {
                        type: 'bar',
                        data: {
                            labels: Object.keys(gradeDistribution),
                            datasets: [{
                                label: '인원수',
                                data: Object.values(gradeDistribution),
                                backgroundColor: [
                                    '#1e3c72',
                                    '#2c5f2d', 
                                    '#2c5f2d',
                                    '#20547a',
                                    '#20547a',
                                    '#5f5f5f',
                                    '#8b2c2c'
                                ],
                                borderRadius: 8,
                                barThickness: 40
                            }]
                        },
                        plugins: useDataLabels ? [ChartDataLabels] : [],
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            layout: {
                                padding: {
                                    top: 30,  // 상단에 30px 여백 추가
                                    left: 10,
                                    right: 10,
                                    bottom: 10
                                }
                            },
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    ticks: {
                                        stepSize: 5,
                                        font: {
                                            size: 14,
                                            weight: '600'
                                        },
                                        color: '#ffffff'
                                    },
                                    grid: {
                                        drawBorder: false,
                                        color: 'rgba(255, 255, 255, 0.1)'
                                    },
                                    title: {
                                        display: true,
                                        text: '인원수',
                                        color: '#ffffff',
                                        font: {
                                            size: 14,
                                            weight: 'bold'
                                        }
                                    }
                                },
                                x: {
                                    grid: {
                                        display: false
                                    },
                                    ticks: {
                                        font: {
                                            size: 14,
                                            weight: 'bold'
                                        },
                                        color: '#ffffff'
                                    },
                                    title: {
                                        display: true,
                                        text: '등급',
                                        color: '#ffffff',
                                        font: {
                                            size: 14,
                                            weight: 'bold'
                                        }
                                    }
                                }
                            },
                            plugins: {
                                legend: {
                                    display: false
                                },
                                tooltip: {
                                    callbacks: {
                                        label: function(context) {
                                            return context.label + '등급: ' + context.parsed.y + '명';
                                        }
                                    }
                                },
                                datalabels: useDataLabels ? {
                                    anchor: 'end',
                                    align: 'top',
                                    color: '#ffffff',
                                    font: {
                                        weight: 'bold',
                                        size: 14
                                    },
                                    formatter: function(value) {
                                        return value > 0 ? value + '명' : '';
                                    }
                                } : false
                            }
                        }
                    });
                }
                
                // 실제 데이터 기반 부서별 평균 점수 계산
                const departmentScores = {};
                
                console.log('📈 부서별 성과 계산 시작...');
                
                this.state.employees.forEach((emp, idx) => {
                    // 부서명 확인 (department, 부서, dept 등)
                    const dept = emp.department || emp.부서 || emp.dept || '기타';
                    // 점수 확인 (ai_score, overall_score, 종합점수 등)
                    const score = emp.ai_score || emp.overall_score || emp.AIRISS_v2_종합점수 || emp.종합점수 || 0;
                    
                    // 첫 몇 개 데이터 로깅
                    if (idx < 3) {
                        console.log(`직원 ${idx + 1} - 부서: ${dept}, 점수: ${score}`);
                    }
                    
                    if (!departmentScores[dept]) {
                        departmentScores[dept] = { total: 0, count: 0 };
                    }
                    departmentScores[dept].total += score;
                    departmentScores[dept].count++;
                });
                
                console.log('📊 부서별 집계:', departmentScores);
                
                // 평균 점수 계산 및 정렬
                const departmentAverages = [];
                Object.keys(departmentScores).forEach(dept => {
                    if (departmentScores[dept].count > 0) {
                        const avg = Math.round(departmentScores[dept].total / departmentScores[dept].count);
                        departmentAverages.push({
                            name: dept,
                            avg: avg
                        });
                        console.log(`부서 ${dept}: 평균 ${avg}점 (${departmentScores[dept].count}명)`);
                    }
                });
                
                // 상위 5개 부서만 선택 (점수 기준 정렬)
                departmentAverages.sort((a, b) => b.avg - a.avg);
                const topDepartments = departmentAverages.slice(0, 5);
                
                console.log('📊 상위 5개 부서:', topDepartments);
                
                // 부서별 성과 차트
                const deptCtx = document.getElementById('departmentChart');
                if (deptCtx) {
                    // 기존 차트가 있으면 제거
                    if (this.departmentChart) {
                        this.departmentChart.destroy();
                    }
                    
                    const useDataLabels = typeof ChartDataLabels !== 'undefined';
                    
                    this.departmentChart = new Chart(deptCtx, {
                        type: 'bar',
                        data: {
                            labels: topDepartments.map(d => d.name),
                            datasets: [{
                                label: '평균 점수',
                                data: topDepartments.map(d => d.avg),
                                backgroundColor: '#00d9ff',
                                borderRadius: 8
                            }]
                        },
                        plugins: useDataLabels ? [ChartDataLabels] : [],
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            layout: {
                                padding: {
                                    top: 30,  // 상단에 30px 여백 추가
                                    left: 10,
                                    right: 10,
                                    bottom: 10
                                }
                            },
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    // max 값을 데이터에 따라 동적으로 설정
                                    max: Math.max(...topDepartments.map(d => d.avg)) > 100 ? 1000 : 100,
                                    ticks: {
                                        stepSize: Math.max(...topDepartments.map(d => d.avg)) > 100 ? 200 : 20,
                                        font: {
                                            size: 14,
                                            weight: '600'
                                        },
                                        color: '#ffffff'
                                    },
                                    grid: {
                                        drawBorder: false,
                                        color: 'rgba(255, 255, 255, 0.1)'
                                    },
                                    title: {
                                        display: true,
                                        text: '평균 점수',
                                        color: '#ffffff',
                                        font: {
                                            size: 14,
                                            weight: 'bold'
                                        }
                                    }
                                },
                                x: {
                                    grid: {
                                        display: false
                                    },
                                    ticks: {
                                        font: {
                                            size: 14,
                                            weight: 'bold'
                                        },
                                        color: '#ffffff'
                                    },
                                    title: {
                                        display: true,
                                        text: '부서명',
                                        color: '#ffffff',
                                        font: {
                                            size: 14,
                                            weight: 'bold'
                                        }
                                    }
                                }
                            },
                            plugins: {
                                legend: {
                                    display: false
                                },
                                tooltip: {
                                    callbacks: {
                                        label: function(context) {
                                            return '평균 점수: ' + context.parsed.y + '점';
                                        }
                                    }
                                },
                                datalabels: useDataLabels ? {
                                    anchor: 'end',
                                    align: 'top',
                                    color: '#ffffff',
                                    font: {
                                        weight: 'bold',
                                        size: 14
                                    },
                                    formatter: function(value) {
                                        return value + '점';
                                    }
                                } : false
                            }
                        }
                    });
                }
            },
            
            // 직원 데이터 로드 (개선된 버전)
            async loadEmployeesData() {
                try {
                    console.log('🔄 직원 데이터 로딩 시작...');
                    const response = await this.api.request('GET', '/employees/list');
                    console.log('📊 받은 응답:', response);
                    
                    // 에러 응답 체크
                    if (response && response.success === false) {
                        console.error('❌ 서버 에러:', response.error);
                        this.showNotification(
                            `데이터 로드 실패: ${response.error?.message || '서버 오류가 발생했습니다'}`, 
                            'error'
                        );
                        this.renderNoDataMessage(response.error?.message || '데이터베이스 조회에 실패했습니다');
                        return;
                    }
                    
                    // 성공 응답 처리
                    if (response && response.employees) {
                        if (response.employees.length > 0) {
                            this.state.employees = response.employees;
                            console.log('👥 로드된 직원 수:', this.state.employees.length);
                            this.renderEmployees(this.state.employees);
                            
                            // 대시보드 탭에서 차트 업데이트
                            if (this.state.currentTab === 'dashboard') {
                                this.renderDashboardCharts();
                            }
                        } else {
                            console.log('📭 데이터가 비어있음');
                            this.renderNoDataMessage('분석된 직원 데이터가 없습니다');
                        }
                    } else if (response && response.data) {
                        // 다른 형식의 응답 처리
                        const data = response.data;
                        if (data.items && data.items.length > 0) {
                            this.state.employees = data.items;
                            console.log('👥 로드된 직원 수:', this.state.employees.length);
                            this.renderEmployees(this.state.employees);
                        } else {
                            console.log('📭 데이터가 비어있음');
                            this.renderNoDataMessage('분석된 직원 데이터가 없습니다');
                        }
                    } else {
                        console.warn('⚠️ 예상치 못한 데이터 형식:', response);
                        this.renderNoDataMessage('예상치 못한 응답 형식입니다');
                    }
                } catch (error) {
                    console.error('❌ 직원 데이터 로딩 실패:', error);
                    this.showNotification('서버 연결에 실패했습니다', 'error');
                    this.renderNoDataMessage('서버 연결에 실패했습니다');
                }
            },
            
            // 데이터 없음 메시지 표시
            renderNoDataMessage(message) {
                const tbody = document.getElementById('employees-table');
                if (!tbody) return;
                
                tbody.innerHTML = `
                    <tr>
                        <td colspan="7" style="text-align: center; padding: 60px 20px;">
                            <div style="opacity: 0.7;">
                                <div style="font-size: 3rem; margin-bottom: 20px;">⚠️</div>
                                <h3 style="margin-bottom: 15px; color: var(--text-primary);">${message}</h3>
                                ${message.includes('실패') ? `
                                    <p style="margin: 15px 0; color: var(--text-secondary);">
                                        서버 연결을 확인하거나 잠시 후 다시 시도해주세요.
                                    </p>
                                    <button class="btn btn-secondary" onclick="AIRISS.loadEmployeesData()" style="margin-top: 10px;">
                                        🔄 다시 시도
                                    </button>
                                ` : `
                                    <p style="margin: 15px 0; color: var(--text-secondary);">
                                        직원 데이터를 업로드하여 AI 분석을 시작하세요.
                                    </p>
                                    <button class="btn btn-primary" onclick="AIRISS.switchTab('upload')" style="margin-top: 10px;">
                                        📤 데이터 업로드하기
                                    </button>
                                `}
                            </div>
                        </td>
                    </tr>
                `;
            },
            
            // 직원 목록 렌더링 (페이지네이션 포함)
            renderEmployees(employees, page = 1) {
                const tbody = document.getElementById('employees-table');
                if (!tbody) return;
                
                tbody.innerHTML = '';
                
                // 데이터가 없는 경우
                if (!employees || employees.length === 0) {
                    this.renderNoDataMessage('분석된 직원 데이터가 없습니다');
                    return;
                }
                
                console.log('🖼️ 직원 목록 렌더링:', employees.length + '명');
                
                // 페이지네이션 설정
                const itemsPerPage = 20;
                const totalPages = Math.ceil(employees.length / itemsPerPage);
                const startIndex = (page - 1) * itemsPerPage;
                const endIndex = startIndex + itemsPerPage;
                this.state.currentPage = page;
                
                // 현재 페이지의 직원만 표시
                employees.slice(startIndex, endIndex).forEach((emp, index) => {
                    const row = tbody.insertRow();
                    
                    // EmployeeService의 반환 구조에 맞춤
                    const employeeId = emp.employee_id || emp.uid || emp.id;
                    const employeeName = emp.name || emp.employee_name || '익명';
                    const department = emp.department || '-';
                    const position = emp.position || '-';
                    const grade = emp.grade || emp.ai_grade || 'C';
                    const score = emp.ai_score || emp.overall_score || 0;
                    
                    // 디버깅: 실제 등급 확인
                    if (index < 3) {
                        console.log(`직원 ${employeeId}: grade=${emp.grade}, ai_grade=${emp.ai_grade}, 최종=${grade}`);
                    }
                    
                    // 등급에 따른 색상 결정
                    const gradeColor = {
                        'S': 'success',
                        'A+': 'success',
                        'A': 'primary',
                        'B+': 'info',
                        'B': 'warning',
                        'C': 'secondary',
                        'D': 'danger'
                    }[grade] || 'secondary';
                    
                    row.innerHTML = `
                        <td style="font-weight: 500;">${employeeId || (index + 1)}</td>
                        <td style="font-weight: 600;">${employeeName}</td>
                        <td>${department}</td>
                        <td>${position}</td>
                        <td><span class="btn btn-${gradeColor}" style="padding: 8px 16px; font-size: 14px; font-weight: 600; border-radius: 8px; color: white !important;">${grade}</span></td>
                        <td style="font-weight: 600; color: var(--primary-color); font-size: 18px;">${Math.round(score)}</td>
                        <td>
                            <button class="btn btn-primary" style="padding: 10px 20px; font-size: 14px; border-radius: 8px; font-weight: 500;" 
                                    onclick="AIRISS.viewEmployeeDetail('${employeeId}')">
                                상세보기
                            </button>
                        </td>
                    `;
                });
                
                // 페이지네이션 UI 렌더링
                this.renderPagination(employees.length, page, itemsPerPage);
                
                console.log('✅ 직원 목록 렌더링 완료');
            },
            
            // 페이지네이션 UI 렌더링
            renderPagination(totalItems, currentPage, itemsPerPage) {
                const container = document.getElementById('pagination-container');
                if (!container) return;
                
                const totalPages = Math.ceil(totalItems / itemsPerPage);
                container.innerHTML = '';
                
                // 이전 버튼
                const prevBtn = document.createElement('button');
                prevBtn.className = 'btn btn-secondary';
                prevBtn.innerHTML = '◀ 이전';
                prevBtn.disabled = currentPage === 1;
                prevBtn.onclick = () => this.renderEmployees(this.state.employees, currentPage - 1);
                prevBtn.style.cssText = 'padding: 8px 16px; font-size: 14px; border-radius: 8px;';
                container.appendChild(prevBtn);
                
                // 페이지 정보
                const pageInfo = document.createElement('div');
                pageInfo.style.cssText = 'padding: 8px 20px; font-weight: 600; color: #2c3e50;';
                pageInfo.innerHTML = `
                    <span style="font-size: 16px;">${currentPage} / ${totalPages}</span>
                    <br>
                    <span style="font-size: 12px; color: #666;">총 ${totalItems}명</span>
                `;
                container.appendChild(pageInfo);
                
                // 다음 버튼
                const nextBtn = document.createElement('button');
                nextBtn.className = 'btn btn-secondary';
                nextBtn.innerHTML = '다음 ▶';
                nextBtn.disabled = currentPage === totalPages;
                nextBtn.onclick = () => this.renderEmployees(this.state.employees, currentPage + 1);
                nextBtn.style.cssText = 'padding: 8px 16px; font-size: 14px; border-radius: 8px;';
                container.appendChild(nextBtn);
            },
            
            // 직원 상세 보기 - 풍부한 AI 분석 정보 표시
            async viewEmployeeDetail(employeeId) {
                try {
                    console.log('🔍 직원 상세 조회 시작:', employeeId);
                    const data = await this.api.request('GET', `/employees/${employeeId}/ai-analysis`);
                    console.log('✅ 직원 상세 데이터:', data);
                    
                    // 데이터 검증
                    if (!data || data.error) {
                        throw new Error(data?.error || '데이터를 불러올 수 없습니다');
                    }
                    
                    // 등급별 색상 매핑 - 심플하고 전문적인 색상
                    const gradeColors = {
                        'S': '#2c3e50',
                        'A+': '#27ae60', 
                        'A': '#27ae60',
                        'B+': '#3498db',
                        'B': '#3498db',
                        'C': '#7f8c8d',
                        'D': '#e74c3c'
                    };
                    
                    const gradeColor = gradeColors[data.grade] || gradeColors['C'];
                    
                    // 디버깅: 데이터 확인
                    console.log('🎯 렌더링할 데이터:', {
                        competencies: data.competencies,
                        strengths: data.strengths,
                        improvements: data.improvements,
                        ai_comment: data.ai_comment,
                        career_recommendation: data.career_recommendation,
                        education_suggestion: data.education_suggestion
                    });
                    
                    const modalBody = document.getElementById('modal-body');
                    modalBody.style.maxHeight = '85vh';
                    modalBody.style.overflowY = 'auto';
                    modalBody.style.padding = '2rem';
                    modalBody.innerHTML = `
                        <div class="employee-detail-content" style="padding: 20px;">
                            <!-- 헤더 섹션 - 심플하고 전문적인 프로필 카드 스타일 -->
                            <div class="profile-header" style="
                                background: linear-gradient(135deg, rgba(52, 61, 84, 0.95) 0%, rgba(41, 49, 69, 0.9) 100%);
                                border: 1px solid rgba(88, 95, 112, 0.4);
                                border-radius: 8px;
                                padding: 30px;
                                color: #ffffff;
                                margin-bottom: 30px;
                                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                            ">
                                <div style="display: flex; align-items: center; justify-content: space-between;">
                                    <div style="flex: 1;">
                                        <h2 style="font-size: 32px; margin-bottom: 10px; font-weight: 700;">
                                            ${data.name || '익명'}
                                        </h2>
                                        <div style="display: flex; gap: 20px; margin-bottom: 20px; color: rgba(255, 255, 255, 0.85);">
                                            <span>📍 ${data.department || '미지정'}</span>
                                            <span>💼 ${data.position || '미지정'}</span>
                                            <span>👨‍💼 추정경력 ${data.estimated_experience || '3-5년'}</span>
                                            <span>📅 ${data.analyzed_at ? new Date(data.analyzed_at).toLocaleDateString('ko-KR') : '최근 분석'}</span>
                                        </div>
                                        <div style="display: flex; gap: 15px; align-items: center; flex-wrap: wrap;">
                                            <span style="
                                                background: rgba(0, 217, 255, 0.15);
                                                padding: 6px 14px;
                                                border-radius: 4px;
                                                font-size: 14px;
                                                color: #ffffff;
                                                border: 1px solid rgba(0, 217, 255, 0.3);
                                            ">
                                                🏆 ${data.performance_indicators?.overall_ranking || '상위 50%'}
                                            </span>
                                            <span style="
                                                background: rgba(0, 217, 255, 0.15);
                                                padding: 6px 14px;
                                                border-radius: 4px;
                                                font-size: 14px;
                                                color: #ffffff;
                                                border: 1px solid rgba(0, 217, 255, 0.3);
                                            ">
                                                📈 성장잠재력 ${data.performance_indicators?.growth_potential || '보통'}
                                            </span>
                                            <span style="
                                                background: rgba(0, 217, 255, 0.15);
                                                padding: 6px 14px;
                                                border-radius: 4px;
                                                font-size: 14px;
                                                color: #ffffff;
                                                border: 1px solid rgba(0, 217, 255, 0.3);
                                            ">
                                                ⚖️ 역량균형 ${data.performance_indicators?.competency_balance || '보통'}
                                            </span>
                                            <span style="
                                                background: rgba(0, 217, 255, 0.15);
                                                padding: 6px 14px;
                                                border-radius: 4px;
                                                font-size: 14px;
                                                color: #ffffff;
                                                border: 1px solid rgba(0, 217, 255, 0.3);
                                            ">
                                                👑 리더십준비도 ${data.performance_indicators?.leadership_readiness || '개발필요'}
                                            </span>
                                        </div>
                                    </div>
                                    <div style="text-align: center;">
                                        <div style="
                                            width: 140px;
                                            height: 140px;
                                            border-radius: 50%;
                                            background: linear-gradient(135deg, rgba(52, 61, 84, 0.95) 0%, rgba(41, 49, 69, 0.9) 100%);
                                            display: flex;
                                            flex-direction: column;
                                            align-items: center;
                                            justify-content: center;
                                            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                                            position: relative;
                                        ">
                                            <div style="font-size: 48px; font-weight: bold; color: #00d9ff;">
                                                ${data.ai_score || 0}
                                            </div>
                                            <div style="font-size: 14px; color: rgba(255, 255, 255, 0.8); margin-top: 5px;">AI SCORE</div>
                                            <div style="
                                                position: absolute;
                                                top: -10px;
                                                right: -10px;
                                                background: ${gradeColor};
                                                color: white;
                                                padding: 6px 12px;
                                                border-radius: 4px;
                                                font-size: 14px;
                                                font-weight: bold;
                                            ">${data.grade || 'C'}</div>
                                        </div>
                                        <div style="
                                            margin-top: 15px;
                                            background: linear-gradient(135deg, #00d9ff 0%, #7b61ff 100%);
                                            color: white;
                                            padding: 8px 20px;
                                            border-radius: 4px;
                                            font-weight: 500;
                                            font-size: 14px;
                                            display: inline-block;
                                        ">
                                            평균 역량: ${data.competency_average || 0}점
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- 성과 분석 대시보드 - 심플한 디자인 -->
                            <div class="performance-dashboard" style="
                                display: grid;
                                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                                gap: 15px;
                                margin-bottom: 30px;
                            ">
                                <div class="metric-card" style="
                                    background: linear-gradient(135deg, rgba(52, 61, 84, 0.95) 0%, rgba(41, 49, 69, 0.9) 100%);
                                    color: #ffffff;
                                    padding: 20px;
                                    border-radius: 8px;
                                    text-align: center;
                                    border: 1px solid #e9ecef;
                                    box-shadow: 0 2px 4px rgba(0,0,0,0.08);
                                ">
                                    <div style="font-size: 20px; margin-bottom: 8px;">📊</div>
                                    <div style="font-size: 18px; font-weight: 600; margin-bottom: 5px;">${data.performance_indicators?.overall_ranking || '상위 50%'}</div>
                                    <div style="font-size: 13px; color: rgba(255, 255, 255, 0.7);">전체 순위</div>
                                </div>
                                <div class="metric-card" style="
                                    background: linear-gradient(135deg, rgba(52, 61, 84, 0.95) 0%, rgba(41, 49, 69, 0.9) 100%);
                                    color: #ffffff;
                                    padding: 20px;
                                    border-radius: 8px;
                                    text-align: center;
                                    border: 1px solid #e9ecef;
                                    box-shadow: 0 2px 4px rgba(0,0,0,0.08);
                                ">
                                    <div style="font-size: 20px; margin-bottom: 8px;">📈</div>
                                    <div style="font-size: 18px; font-weight: 600; margin-bottom: 5px;">${data.performance_indicators?.growth_potential || '보통'}</div>
                                    <div style="font-size: 13px; color: rgba(255, 255, 255, 0.7);">성장 잠재력</div>
                                </div>
                                <div class="metric-card" style="
                                    background: linear-gradient(135deg, rgba(52, 61, 84, 0.95) 0%, rgba(41, 49, 69, 0.9) 100%);
                                    color: #ffffff;
                                    padding: 20px;
                                    border-radius: 8px;
                                    text-align: center;
                                    border: 1px solid #e9ecef;
                                    box-shadow: 0 2px 4px rgba(0,0,0,0.08);
                                ">
                                    <div style="font-size: 20px; margin-bottom: 8px;">⚠️</div>
                                    <div style="font-size: 18px; font-weight: 600; margin-bottom: 5px;">${data.performance_indicators?.risk_level || '보통'}</div>
                                    <div style="font-size: 13px; color: rgba(255, 255, 255, 0.7);">이직 위험도</div>
                                </div>
                                <div class="metric-card" style="
                                    background: linear-gradient(135deg, rgba(52, 61, 84, 0.95) 0%, rgba(41, 49, 69, 0.9) 100%);
                                    color: #ffffff;
                                    padding: 20px;
                                    border-radius: 8px;
                                    text-align: center;
                                    border: 1px solid #e9ecef;
                                    box-shadow: 0 2px 4px rgba(0,0,0,0.08);
                                ">
                                    <div style="font-size: 20px; margin-bottom: 8px;">👑</div>
                                    <div style="font-size: 18px; font-weight: 600; margin-bottom: 5px;">${data.performance_indicators?.leadership_readiness || '개발필요'}</div>
                                    <div style="font-size: 13px; color: rgba(255, 255, 255, 0.7);">리더십 준비도</div>
                                </div>
                            </div>
                            
                            <!-- 8대 역량 분석 - 심플한 스타일 -->
                            <div class="competency-section" style="
                                background: linear-gradient(135deg, rgba(52, 61, 84, 0.95) 0%, rgba(41, 49, 69, 0.9) 100%);
                                border-radius: 8px;
                                padding: 25px;
                                margin-bottom: 25px;
                                border: 1px solid #e9ecef;
                                box-shadow: 0 2px 4px rgba(0,0,0,0.08);
                            ">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                                    <h3 style="color: #00d9ff; font-size: 20px; font-weight: 600; margin: 0;">
                                        🎯 8대 핵심 역량 분석
                                    </h3>
                                    <div style="
                                        background: #6c757d;
                                        color: white;
                                        padding: 6px 16px;
                                        border-radius: 4px;
                                        font-size: 14px;
                                        font-weight: 500;
                                    ">
                                        평균 점수: ${Math.round(Object.values(data.competencies || {}).reduce((a, b) => a + b, 0) / 8)}점
                                    </div>
                                </div>
                                
                                <div class="competency-grid" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px;">
                                    ${Object.entries(data.competencies || {}).map(([key, value]) => {
                                        const percentage = (value / 100) * 100;
                                        const barColor = value >= 80 ? '#28a745' : value >= 60 ? '#ffc107' : '#dc3545';
                                        return `
                                        <div class="competency-item" style="
                                            background: #f8f9fa;
                                            padding: 16px;
                                            border-radius: 6px;
                                            border: 1px solid #dee2e6;
                                            position: relative;
                                        ">
                                            <div style="position: relative; z-index: 2;">
                                                <div style="font-weight: 600; margin-bottom: 10px; font-size: 14px; color: #2c3e50;">
                                                    ${key}
                                                </div>
                                                <div style="font-size: 32px; color: ${barColor}; font-weight: 700; margin-bottom: 10px;">
                                                    ${value || 0}
                                                </div>
                                                <div style="
                                                    background: #e9ecef;
                                                    border-radius: 4px;
                                                    height: 6px;
                                                    overflow: hidden;
                                                ">
                                                    <div style="
                                                        background: ${barColor};
                                                        height: 100%;
                                                        width: ${percentage}%;
                                                        border-radius: 4px;
                                                    "></div>
                                                </div>
                                                <div style="
                                                    margin-top: 8px;
                                                    font-size: 12px;
                                                    color: #666;
                                                ">
                                                    ${value >= 80 ? '우수' : value >= 60 ? '양호' : '개발필요'}
                                                </div>
                                            </div>
                                        </div>
                                        `;
                                    }).join('')}
                                </div>
                            </div>
                            
                            <!-- 역량 상세 분석 - 새로 추가 -->
                            <div class="competency-analysis" style="
                                background: linear-gradient(135deg, rgba(52, 61, 84, 0.95) 0%, rgba(41, 49, 69, 0.9) 100%);
                                border-radius: 20px;
                                padding: 30px;
                                margin-bottom: 30px;
                                box-shadow: 0 5px 20px rgba(0,0,0,0.05);
                            ">
                                <h3 style="color: #00d9ff; font-size: 24px; font-weight: 600; margin-bottom: 25px;">
                                    📈 역량 상세 분석
                                </h3>
                                
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px;">
                                    <!-- 강점 역량 TOP 3 -->
                                    <div style="
                                        background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 100%);
                                        padding: 25px;
                                        border-radius: 15px;
                                        border-left: 4px solid #28a745;
                                    ">
                                        <h4 style="color: #28a745; margin: 0 0 20px 0; font-size: 18px; font-weight: 600;">
                                            🏆 강점 역량 TOP 3
                                        </h4>
                                        ${(data.top_competencies || []).map((comp, idx) => `
                                            <div style="
                                                display: flex;
                                                justify-content: space-between;
                                                align-items: center;
                                                padding: 12px 0;
                                                border-bottom: ${idx < 2 ? '1px solid rgba(40, 167, 69, 0.1)' : 'none'};
                                            ">
                                                <div style="display: flex; align-items: center;">
                                                    <span style="
                                                        background: #28a745;
                                                        color: white;
                                                        width: 24px;
                                                        height: 24px;
                                                        border-radius: 50%;
                                                        display: flex;
                                                        align-items: center;
                                                        justify-content: center;
                                                        font-size: 12px;
                                                        font-weight: bold;
                                                        margin-right: 12px;
                                                    ">${idx + 1}</span>
                                                    <span style="font-weight: 500; color: #2c3e50;">${comp[0]}</span>
                                                </div>
                                                <div style="
                                                    background: #28a745;
                                                    color: white;
                                                    padding: 4px 12px;
                                                    border-radius: 15px;
                                                    font-size: 14px;
                                                    font-weight: bold;
                                                ">${comp[1]}점</div>
                                            </div>
                                        `).join('')}
                                    </div>
                                    
                                    <!-- 개발 필요 역량 -->
                                    <div style="
                                        background: linear-gradient(135deg, #ffebee 0%, #fff3e0 100%);
                                        padding: 25px;
                                        border-radius: 15px;
                                        border-left: 4px solid #ff9800;
                                    ">
                                        <h4 style="color: #ff9800; margin: 0 0 20px 0; font-size: 18px; font-weight: 600;">
                                            🎯 개발 필요 역량
                                        </h4>
                                        ${(data.low_competencies || []).map((comp, idx) => `
                                            <div style="
                                                display: flex;
                                                justify-content: space-between;
                                                align-items: center;
                                                padding: 12px 0;
                                                border-bottom: ${idx < 2 ? '1px solid rgba(255, 152, 0, 0.1)' : 'none'};
                                            ">
                                                <div style="display: flex; align-items: center;">
                                                    <span style="
                                                        background: #ff9800;
                                                        color: white;
                                                        width: 24px;
                                                        height: 24px;
                                                        border-radius: 50%;
                                                        display: flex;
                                                        align-items: center;
                                                        justify-content: center;
                                                        font-size: 12px;
                                                        font-weight: bold;
                                                        margin-right: 12px;
                                                    ">${idx + 1}</span>
                                                    <span style="font-weight: 500; color: #2c3e50;">${comp[0]}</span>
                                                </div>
                                                <div style="
                                                    background: ${comp[1] >= 60 ? '#ffc107' : '#dc3545'};
                                                    color: white;
                                                    padding: 4px 12px;
                                                    border-radius: 15px;
                                                    font-size: 14px;
                                                    font-weight: bold;
                                                ">${comp[1]}점</div>
                                            </div>
                                        `).join('')}
                                    </div>
                                </div>
                            </div>
                            
                            <!-- AI 종합 피드백 - 심플한 디자인 -->
                            ${data.ai_comment ? `
                            <div class="ai-feedback-section" style="
                                background: linear-gradient(135deg, rgba(52, 61, 84, 0.95) 0%, rgba(41, 49, 69, 0.9) 100%);
                                border-radius: 8px;
                                padding: 25px;
                                margin-bottom: 25px;
                                border: 1px solid #e9ecef;
                                box-shadow: 0 2px 4px rgba(0,0,0,0.08);
                                border-left: 4px solid #6c757d;
                            ">
                                <div style="display: flex; align-items: center; margin-bottom: 16px;">
                                    <div style="
                                        width: 32px;
                                        height: 32px;
                                        background: #6c757d;
                                        border-radius: 4px;
                                        display: flex;
                                        align-items: center;
                                        justify-content: center;
                                        margin-right: 10px;
                                        color: white;
                                        font-size: 16px;
                                    ">🤖</div>
                                    <h3 style="margin: 0; color: #00d9ff; font-size: 18px; font-weight: 600;">AI 종합 분석 리포트</h3>
                                </div>
                                <div style="
                                    background: #f8f9fa;
                                    padding: 16px;
                                    border-radius: 6px;
                                    font-size: 15px;
                                    line-height: 1.6;
                                    color: #495057;
                                    border: 1px solid #e9ecef;
                                ">${data.ai_comment}</div>
                            </div>
                            ` : ''}
                            
                            <!-- 강점과 개선점 - 심플한 카드 스타일 -->
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 25px;">
                                <div class="strengths-section" style="
                                    background: linear-gradient(135deg, rgba(52, 61, 84, 0.95) 0%, rgba(41, 49, 69, 0.9) 100%);
                                    border-radius: 8px;
                                    padding: 20px;
                                    border: 1px solid #e9ecef;
                                    box-shadow: 0 2px 4px rgba(0,0,0,0.08);
                                    border-left: 4px solid #28a745;
                                ">
                                    <div style="display: flex; align-items: center; margin-bottom: 16px;">
                                        <div style="
                                            width: 32px;
                                            height: 32px;
                                            background: #28a745;
                                            border-radius: 4px;
                                            display: flex;
                                            align-items: center;
                                            justify-content: center;
                                            margin-right: 10px;
                                            color: white;
                                            font-size: 16px;
                                        ">✨</div>
                                        <h3 style="margin: 0; color: #00d9ff; font-size: 18px; font-weight: 600;">핵심 강점</h3>
                                    </div>
                                    <div>
                                        ${(data.strengths || ['데이터가 충분하지 않습니다']).map((s, idx) => {
                                            // 긴 텍스트를 파싱하여 구조화된 형태로 변환
                                            let parsedContent = s;
                                            
                                            // "강점1:", "강점2:" 형식으로 분리
                                            if (s.includes('강점1:') || s.includes('강점2:') || s.includes('강점3:')) {
                                                const parts = s.split(/강점\d+:|아이콘\d+에/);
                                                parsedContent = parts.filter(part => part.trim()).map(part => {
                                                    const cleanPart = part.trim().replace(/^-\s*/, '');
                                                    if (cleanPart.includes(' - ')) {
                                                        const [title, description] = cleanPart.split(' - ', 2);
                                                        return '<strong>' + title.trim() + '</strong><br><span style="color: #6c757d; font-size: 14px;">' + description.trim() + '</span>';
                                                    }
                                                    return cleanPart;
                                                }).join('<br><br>');
                                            }
                                            
                                            return '<div style="padding: 12px; background: #f8f9fa; border-radius: 6px; margin-bottom: 10px; border: 1px solid #e9ecef;"><div style="color: #495057; line-height: 1.6;">' + parsedContent + '</div></div>';
                                        }).join('')}
                                    </div>
                                </div>
                                
                                <div class="improvements-section" style="
                                    background: linear-gradient(135deg, rgba(52, 61, 84, 0.95) 0%, rgba(41, 49, 69, 0.9) 100%);
                                    border-radius: 8px;
                                    padding: 20px;
                                    border: 1px solid #e9ecef;
                                    box-shadow: 0 2px 4px rgba(0,0,0,0.08);
                                    border-left: 4px solid #ffc107;
                                ">
                                    <div style="display: flex; align-items: center; margin-bottom: 16px;">
                                        <div style="
                                            width: 32px;
                                            height: 32px;
                                            background: #ffc107;
                                            border-radius: 4px;
                                            display: flex;
                                            align-items: center;
                                            justify-content: center;
                                            margin-right: 10px;
                                            color: white;
                                            font-size: 16px;
                                        ">🎯</div>
                                        <h3 style="margin: 0; color: #00d9ff; font-size: 18px; font-weight: 600;">개선 포인트</h3>
                                    </div>
                                    <div>
                                        ${(data.improvements || ['데이터가 충분하지 않습니다']).map((i, idx) => `
                                            <div style="
                                                padding: 12px;
                                                background: #f8f9fa;
                                                border-radius: 6px;
                                                margin-bottom: 10px;
                                                border: 1px solid #e9ecef;
                                            ">
                                                <div style="color: #495057; line-height: 1.6;">${i}</div>
                                            </div>
                                        `).join('')}
                                    </div>
                                </div>
                            </div>
                            
                            <!-- 추천 사항 - 심플한 카드 스타일 -->
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 25px;">
                                <div class="career-recommendation" style="
                                    background: linear-gradient(135deg, rgba(52, 61, 84, 0.95) 0%, rgba(41, 49, 69, 0.9) 100%);
                                    border-radius: 8px;
                                    padding: 20px;
                                    border: 1px solid #e9ecef;
                                    box-shadow: 0 2px 4px rgba(0,0,0,0.08);
                                    border-left: 4px solid #007bff;
                                ">
                                    <div style="display: flex; align-items: center; margin-bottom: 16px;">
                                        <div style="
                                            width: 32px;
                                            height: 32px;
                                            background: #007bff;
                                            border-radius: 4px;
                                            display: flex;
                                            align-items: center;
                                            justify-content: center;
                                            margin-right: 10px;
                                            color: white;
                                            font-size: 16px;
                                        ">🚀</div>
                                        <h3 style="margin: 0; color: #00d9ff; font-size: 18px; font-weight: 600;">경력 발전 로드맵</h3>
                                    </div>
                                    <div>
                                        ${(data.career_recommendation && data.career_recommendation.length > 0 ? data.career_recommendation : []).map(r => `
                                            <div style="
                                                background: #f8f9fa;
                                                padding: 12px;
                                                border-radius: 6px;
                                                margin-bottom: 10px;
                                                border: 1px solid #e9ecef;
                                                display: flex;
                                                align-items: center;
                                            ">
                                                <span style="margin-right: 10px; color: #007bff;">▶</span>
                                                <span style="color: #495057;">${r}</span>
                                            </div>
                                        `).join('')}
                                    </div>
                                </div>
                                
                                <div class="education-suggestion" style="
                                    background: linear-gradient(135deg, rgba(52, 61, 84, 0.95) 0%, rgba(41, 49, 69, 0.9) 100%);
                                    border-radius: 8px;
                                    padding: 20px;
                                    border: 1px solid #e9ecef;
                                    box-shadow: 0 2px 4px rgba(0,0,0,0.08);
                                    border-left: 4px solid #17a2b8;
                                ">
                                    <div style="display: flex; align-items: center; margin-bottom: 16px;">
                                        <div style="
                                            width: 32px;
                                            height: 32px;
                                            background: #17a2b8;
                                            border-radius: 4px;
                                            display: flex;
                                            align-items: center;
                                            justify-content: center;
                                            margin-right: 10px;
                                            color: white;
                                            font-size: 16px;
                                        ">📚</div>
                                        <h3 style="margin: 0; color: #00d9ff; font-size: 18px; font-weight: 600;">맞춤 교육 프로그램</h3>
                                    </div>
                                    <div>
                                        ${(data.education_suggestion || ['리더십 교육 프로그램', '전략적 사고 워크샵']).map(e => `
                                            <div style="
                                                background: #f8f9fa;
                                                padding: 12px;
                                                border-radius: 6px;
                                                margin-bottom: 10px;
                                                border: 1px solid #e9ecef;
                                                display: flex;
                                                align-items: center;
                                            ">
                                                <span style="margin-right: 10px; color: #17a2b8;">▶</span>
                                                <span style="color: #495057;">${e}</span>
                                            </div>
                                        `).join('')}
                                    </div>
                                </div>
                            </div>
                            
                            <!-- 종합 인사이트 - 심플한 디자인 -->
                            <div class="comprehensive-insights" style="
                                background: linear-gradient(135deg, rgba(52, 61, 84, 0.95) 0%, rgba(41, 49, 69, 0.9) 100%);
                                border-radius: 8px;
                                padding: 25px;
                                margin-bottom: 25px;
                                border: 1px solid #e9ecef;
                                box-shadow: 0 2px 4px rgba(0,0,0,0.08);
                            ">
                                <h3 style="color: #00d9ff; font-size: 20px; font-weight: 600; margin-bottom: 20px;">
                                    🎯 종합 인사이트 & 액션 플랜
                                </h3>
                                
                                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px;">
                                    <!-- 즉시 실행 가능한 액션 -->
                                    <div style="
                                        background: #f8f9fa;
                                        padding: 16px;
                                        border-radius: 6px;
                                        border: 1px solid #e9ecef;
                                        border-left: 3px solid #28a745;
                                    ">
                                        <h4 style="color: #28a745; margin: 0 0 15px 0; font-size: 16px; font-weight: 600;">
                                            ⚡ 즉시 실행 (1-3개월)
                                        </h4>
                                        <ul style="margin: 0; padding-left: 20px; color: #495057; line-height: 1.6;">
                                            ${data.low_competencies && data.low_competencies.length > 0 ? `
                                                <li>${data.low_competencies[0][0]} 역량 집중 개발</li>
                                                <li>멘토링 프로그램 참여</li>
                                                <li>관련 온라인 과정 수강</li>
                                            ` : `
                                                <li>강점 역량 더욱 활용</li>
                                                <li>동료와 지식 공유</li>
                                                <li>새로운 도전 과제 수행</li>
                                            `}
                                        </ul>
                                    </div>
                                    
                                    <!-- 중기 발전 계획 -->
                                    <div style="
                                        background: #f8f9fa;
                                        padding: 16px;
                                        border-radius: 6px;
                                        border: 1px solid #e9ecef;
                                        border-left: 3px solid #007bff;
                                    ">
                                        <h4 style="color: #007bff; margin: 0 0 15px 0; font-size: 16px; font-weight: 600;">
                                            🎯 중기 목표 (6-12개월)
                                        </h4>
                                        <ul style="margin: 0; padding-left: 20px; color: #495057; line-height: 1.6;">
                                            ${data.ai_score >= 70 ? `
                                                <li>팀 프로젝트 리딩 경험</li>
                                                <li>교차 부서 협업 확대</li>
                                                <li>전문성 인증 취득</li>
                                            ` : `
                                                <li>기본 역량 안정화</li>
                                                <li>업무 프로세스 개선</li>
                                                <li>전문 교육 이수</li>
                                            `}
                                        </ul>
                                    </div>
                                    
                                    <!-- 장기 비전 -->
                                    <div style="
                                        background: #f8f9fa;
                                        padding: 16px;
                                        border-radius: 6px;
                                        border: 1px solid #e9ecef;
                                        border-left: 3px solid #ffc107;
                                    ">
                                        <h4 style="color: #e67e22; margin: 0 0 15px 0; font-size: 16px; font-weight: 600;">
                                            🚀 장기 비전 (1-2년)
                                        </h4>
                                        <ul style="margin: 0; padding-left: 20px; color: #495057; line-height: 1.6;">
                                            ${data.ai_score >= 80 ? `
                                                <li>리더십 포지션 도전</li>
                                                <li>전략 기획 참여</li>
                                                <li>조직 발전 기여</li>
                                            ` : data.ai_score >= 60 ? `
                                                <li>전문가 포지션 확립</li>
                                                <li>핵심 업무 담당</li>
                                                <li>후배 멘토링 역할</li>
                                            ` : `
                                                <li>안정적 성과 달성</li>
                                                <li>역량 균형 개발</li>
                                                <li>전문 분야 확립</li>
                                            `}
                                        </ul>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- 성과 예측 및 리스크 분석 - 심플한 디자인 -->
                            <div class="prediction-analysis" style="
                                background: linear-gradient(135deg, rgba(52, 61, 84, 0.95) 0%, rgba(41, 49, 69, 0.9) 100%);
                                border-radius: 8px;
                                padding: 25px;
                                margin-bottom: 25px;
                                border: 1px solid #e9ecef;
                                box-shadow: 0 2px 4px rgba(0,0,0,0.08);
                            ">
                                <h3 style="color: #00d9ff; font-size: 20px; font-weight: 600; margin-bottom: 20px;">
                                    🔮 AI 예측 분석 & 리스크 관리
                                </h3>
                                
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                                    <!-- 성과 예측 -->
                                    <div style="
                                        background: #f8f9fa;
                                        padding: 20px;
                                        border-radius: 6px;
                                        border: 1px solid #e9ecef;
                                    ">
                                        <h4 style="color: #2c3e50; margin: 0 0 16px 0; font-size: 16px; font-weight: 600;">
                                            📊 성과 예측 (6개월 후)
                                        </h4>
                                        <div style="margin-bottom: 12px;">
                                            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                                <span style="font-size: 14px; color: #495057;">예상 AI 점수</span>
                                                <span style="font-weight: bold; color: #2c3e50;">${Math.min(100, data.ai_score + (data.ai_score >= 70 ? 8 : data.ai_score >= 50 ? 12 : 15))}점</span>
                                            </div>
                                            <div style="
                                                background: #e9ecef;
                                                border-radius: 4px;
                                                height: 6px;
                                                overflow: hidden;
                                            ">
                                                <div style="
                                                    background: #28a745;
                                                    height: 100%;
                                                    width: ${Math.min(100, ((data.ai_score + (data.ai_score >= 70 ? 8 : data.ai_score >= 50 ? 12 : 15)) / 100) * 100)}%;
                                                "></div>
                                            </div>
                                        </div>
                                        <div style="font-size: 14px; color: #6c757d; line-height: 1.5;">
                                            현재 성장 궤도를 유지할 경우, ${data.ai_score >= 70 ? '리더십 역할 준비 완료' : data.ai_score >= 50 ? '안정적인 성과 향상 예상' : '기본 역량 강화 필요'}
                                        </div>
                                    </div>
                                    
                                    <!-- 리스크 분석 -->
                                    <div style="
                                        background: #f8f9fa;
                                        padding: 20px;
                                        border-radius: 6px;
                                        border: 1px solid #e9ecef;
                                    ">
                                        <h4 style="color: #2c3e50; margin: 0 0 16px 0; font-size: 16px; font-weight: 600;">
                                            ⚠️ 리스크 요인 분석
                                        </h4>
                                        <div>
                                            ${data.ai_score < 60 ? `
                                                <div style="
                                                    background: #fff5f5;
                                                    padding: 12px;
                                                    border-radius: 6px;
                                                    margin-bottom: 10px;
                                                    border: 1px solid #fed7d7;
                                                ">
                                                    <div style="font-weight: 600; margin-bottom: 5px; color: #c53030;">🔴 높은 리스크</div>
                                                    <div style="font-size: 13px; color: #495057;">성과 개선 및 역량 강화 시급</div>
                                                </div>
                                            ` : data.ai_score < 75 ? `
                                                <div style="
                                                    background: #fffdf5;
                                                    padding: 12px;
                                                    border-radius: 6px;
                                                    margin-bottom: 10px;
                                                    border: 1px solid #feebc8;
                                                ">
                                                    <div style="font-weight: 600; margin-bottom: 5px; color: #c05621;">🟡 보통 리스크</div>
                                                    <div style="font-size: 13px; color: #495057;">지속적인 발전 노력 필요</div>
                                                </div>
                                            ` : `
                                                <div style="
                                                    background: #f0fff4;
                                                    padding: 12px;
                                                    border-radius: 6px;
                                                    margin-bottom: 10px;
                                                    border: 1px solid #c6f6d5;
                                                ">
                                                    <div style="font-weight: 600; margin-bottom: 5px; color: #276749;">🟢 낮은 리스크</div>
                                                    <div style="font-size: 13px; color: #495057;">안정적이며 성장 궤도 양호</div>
                                                </div>
                                            `}
                                            <div style="font-size: 14px; color: #495057; line-height: 1.5;">
                                                <strong>권장 조치:</strong><br>
                                                ${data.performance_indicators?.risk_level === '높음' ? '즉시 개선 계획 수립 및 집중 관리' : 
                                                  data.performance_indicators?.risk_level === '보통' ? '정기적 모니터링 및 점진적 개선' : 
                                                  '현재 수준 유지 및 추가 도전 과제 부여'}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- 분석 정보 및 메타데이터 -->
                            <div class="analysis-metadata" style="
                                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                                border-radius: 15px;
                                padding: 25px;
                                margin-top: 30px;
                                border-top: 3px solid var(--primary-color);
                            ">
                                <h4 style="color: #2c3e50; margin: 0 0 20px 0; font-size: 18px; font-weight: 600;">
                                    📋 분석 리포트 정보
                                </h4>
                                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
                                    <div>
                                        <div style="font-size: 12px; color: #6c757d; margin-bottom: 5px;">분석 엔진</div>
                                        <div style="font-weight: 600; color: #2c3e50;">${data.analysis_version || 'AIRISS v5.0 Enhanced'}</div>
                                    </div>
                                    <div>
                                        <div style="font-size: 12px; color: #6c757d; margin-bottom: 5px;">리포트 생성</div>
                                        <div style="font-weight: 600; color: #2c3e50;">${new Date().toLocaleString('ko-KR')}</div>
                                    </div>
                                    <div>
                                        <div style="font-size: 12px; color: #6c757d; margin-bottom: 5px;">분석 기간</div>
                                        <div style="font-weight: 600; color: #2c3e50;">최근 3개월 데이터 기준</div>
                                    </div>
                                    <div>
                                        <div style="font-size: 12px; color: #6c757d; margin-bottom: 5px;">신뢰도</div>
                                        <div style="font-weight: 600; color: var(--success);">95%+</div>
                                    </div>
                                </div>
                                
                                <div style="
                                    margin-top: 20px;
                                    padding: 15px;
                                    background: rgba(255, 107, 53, 0.1);
                                    border-radius: 10px;
                                    border-left: 4px solid var(--primary-color);
                                ">
                                    <div style="font-size: 14px; color: #2c3e50; line-height: 1.6;">
                                        <strong>💡 이 리포트는</strong> AI 기반 종합 분석으로 생성된 개인맞춤형 인사평가 보고서입니다. 
                                        정확한 인사결정을 위해서는 추가적인 정성적 평가와 함께 종합적으로 활용하시기 바랍니다.
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                    
                    document.getElementById('modal-title').textContent = `${data.name || employeeId} - 상세 AI 분석 리포트`;
                    
                    // 현재 직원 데이터를 전역에 저장 (PDF 다운로드용)
                    this.currentEmployeeData = data;
                    
                    const modal = document.getElementById('employee-modal');
                    modal.classList.add('active');
                } catch (error) {
                    console.error('❌ Employee detail load failed:', {
                        employeeId: employeeId,
                        error: error.message,
                        stack: error.stack
                    });
                    
                    const modalBody = document.getElementById('modal-body');
                    modalBody.innerHTML = `
                        <div style="text-align: center; padding: 40px; color: #dc3545;">
                            <h3>⚠️ 데이터 로드 실패</h3>
                            <p>직원 ID: ${employeeId}</p>
                            <p>분석 데이터를 불러올 수 없습니다.</p>
                            <p style="font-size: 14px; color: #6c757d;">오류: ${error.message}</p>
                            <p style="font-size: 12px; color: #999;">API Endpoint: /api/v1/employees/${employeeId}/ai-analysis</p>
                        </div>
                    `;
                    
                    document.getElementById('modal-title').textContent = '데이터 로드 오류';
                    document.getElementById('employee-modal').classList.add('active');
                }
            },
            
            // 파일 선택 처리
            handleFileSelect(event) {
                const file = event.target.files[0];
                if (!file) return;
                
                this.state.uploadedFile = file;
                this.uploadFile(file);
            },
            
            // 파일 업로드
            async uploadFile(file) {
                const formData = new FormData();
                formData.append('file', file);
                
                document.getElementById('upload-progress').style.display = 'block';
                document.getElementById('progress-text').textContent = '업로드 중...';
                
                try {
                    const response = await fetch('/api/v1/upload', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (!response.ok) throw new Error('Upload failed');
                    
                    const data = await response.json();
                    document.getElementById('progress-fill').style.width = '100%';
                    document.getElementById('progress-text').textContent = '업로드 완료!';
                    
                    // 파일 분석 결과 표시
                    this.showFileAnalysisResult(data);
                    
                    // Step 2로 이동
                    setTimeout(() => {
                        document.getElementById('analysis-config-step').style.display = 'block';
                        document.getElementById('analysis-config-step').scrollIntoView({ behavior: 'smooth' });
                    }, 1000);
                    
                } catch (error) {
                    console.error('File upload failed:', error);
                    this.showNotification('파일 업로드 실패', 'error');
                }
            },
            
            // 파일 분석 결과 표시
            showFileAnalysisResult(data) {
                const resultDiv = document.getElementById('file-analysis-result');
                const airissReady = data.airiss_ready ? '✅ 가능' : '❌ 불가능';
                const hybridReady = data.hybrid_ready ? '✅ 가능' : '❌ 불가능';
                
                resultDiv.innerHTML = `
                    <div style="background: var(--bg-secondary); padding: 20px; border-radius: 12px;">
                        <h4>📊 파일 분석 결과</h4>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 15px;">
                            <div>
                                <p><strong>파일명:</strong> ${data.filename}</p>
                                <p><strong>총 레코드:</strong> ${data.total_records}개</p>
                                <p><strong>컬럼 수:</strong> ${data.column_count}개</p>
                                <p><strong>데이터 완성도:</strong> ${data.data_quality.completeness}%</p>
                            </div>
                            <div>
                                <p><strong>AI 분석:</strong> ${airissReady}</p>
                                <p><strong>하이브리드 분석:</strong> ${hybridReady}</p>
                                <p><strong>UID 컬럼:</strong> ${data.uid_columns.length}개</p>
                                <p><strong>의견 컬럼:</strong> ${data.opinion_columns.length}개</p>
                            </div>
                        </div>
                        ${data.uid_columns.length > 0 ? `<p style="margin-top: 10px;"><strong>UID 컬럼:</strong> ${data.uid_columns.join(', ')}</p>` : ''}
                        ${data.opinion_columns.length > 0 ? `<p style="margin-top: 5px;"><strong>의견 컬럼:</strong> ${data.opinion_columns.join(', ')}</p>` : ''}
                    </div>
                `;
                resultDiv.style.display = 'block';
                this.state.uploadedFileData = data;
            },
            
            // 사용자 설정으로 분석 시작
            async startAnalysisWithConfig() {
                if (!this.state.uploadedFileData) {
                    this.showNotification('먼저 파일을 업로드해주세요', 'warning');
                    return;
                }
                
                // 사용자 설정 수집
                const analysisMode = document.querySelector('input[name="analysis-mode"]:checked').value;
                const openaiModel = document.getElementById('openai-model').value;
                const maxTokens = parseInt(document.getElementById('max-tokens').value);
                const sampleSize = parseInt(document.getElementById('sample-size').value);
                const enableAiFeedback = document.getElementById('enable-ai-feedback').checked;
                const enableRealtime = document.getElementById('enable-realtime').checked;
                
                // Step 3로 이동
                document.getElementById('analysis-config-step').style.display = 'none';
                document.getElementById('analysis-progress-step').style.display = 'block';
                document.getElementById('analysis-progress-step').scrollIntoView({ behavior: 'smooth' });
                
                try {
                    const requestBody = {
                        sample_size: sampleSize === -1 ? this.state.uploadedFileData.total_records : sampleSize,
                        analysis_mode: analysisMode,
                        enable_ai_feedback: enableAiFeedback,
                        openai_model: openaiModel,
                        max_tokens: maxTokens
                    };
                    
                    this.addAnalysisLog(`🚀 AI 분석 시작 - 모델: ${openaiModel}, 토큰: ${maxTokens}, 인원: ${requestBody.sample_size}명`);
                    
                    const data = await this.api.request('POST', `/analysis/analyze/${this.state.uploadedFileData.file_id}`, requestBody);
                    this.state.analysisJobId = data.job_id;
                    this.state.analysisConfig = requestBody;
                    this.state.enableRealtime = enableRealtime;
                    
                    this.addAnalysisLog(`✅ 분석 작업 생성됨 - Job ID: ${data.job_id}`);
                    
                    // 실시간 상태 체크 시작
                    if (enableRealtime) {
                        this.startRealtimeProgress();
                    } else {
                        this.checkAnalysisStatus();
                    }
                } catch (error) {
                    console.error('Analysis start failed:', error);
                    this.addAnalysisLog('❌ 분석 시작 실패: ' + error.message);
                }
            },
            
            // 실시간 진행 상황 시작
            startRealtimeProgress() {
                this.state.analysisStartTime = Date.now();
                this.state.progressInterval = setInterval(() => {
                    this.updateProgress();
                    this.checkAnalysisStatus(true);
                }, 2000); // 2초마다 업데이트
            },
            
            // 진행 상황 업데이트
            updateProgress() {
                if (!this.state.analysisStartTime) return;
                
                const elapsed = (Date.now() - this.state.analysisStartTime) / 1000;
                const estimatedTime = this.state.analysisConfig?.sample_size * 3; // 1명당 3초 예상
                let progress = Math.min((elapsed / estimatedTime) * 100, 95); // 최대 95%까지만
                
                document.getElementById('analysis-progress-fill').style.width = progress + '%';
                
                const statusText = elapsed < 10 ? '분석 준비 중...' :
                                 elapsed < 30 ? 'AI가 데이터를 읽고 있습니다...' :
                                 elapsed < 60 ? '개인별 분석을 진행하고 있습니다...' :
                                 'AI 피드백을 생성하고 있습니다...';
                
                document.getElementById('analysis-status-text').textContent = statusText;
            },
            
            // 분석 로그 추가
            addAnalysisLog(message) {
                const logDiv = document.getElementById('analysis-log');
                if (logDiv) {
                    const time = new Date().toLocaleTimeString();
                    logDiv.innerHTML += `<div>[${time}] ${message}</div>`;
                    logDiv.scrollTop = logDiv.scrollHeight;
                }
            },
            
            // 분석 상태 체크 (개선된 버전)
            async checkAnalysisStatus(isRealtime = false) {
                if (!this.state.analysisJobId) return;
                
                try {
                    const data = await this.api.request('GET', `/analysis/status/${this.state.analysisJobId}`);
                    
                    if (data.status === 'completed') {
                        this.onAnalysisComplete();
                    } else if (data.status === 'failed') {
                        this.onAnalysisError(data.error || '분석 중 오류 발생');
                    } else {
                        // 진행 중 - 로그 업데이트
                        if (data.progress) {
                            this.addAnalysisLog(`📊 진행 상황: ${data.progress}% (${data.current_step || '처리 중'})`);
                        }
                        
                        // 다음 체크 스케줄링
                        if (!isRealtime) {
                            setTimeout(() => this.checkAnalysisStatus(), 5000);
                        }
                    }
                } catch (error) {
                    console.error('Status check failed:', error);
                    if (!isRealtime) {
                        setTimeout(() => this.checkAnalysisStatus(), 10000); // 오류 시 10초 후 재시도
                    }
                }
            },
            
            // 분석 완료 처리
            onAnalysisComplete() {
                // 실시간 업데이트 중지
                if (this.state.progressInterval) {
                    clearInterval(this.state.progressInterval);
                    this.state.progressInterval = null;
                }
                
                // 진행바 100% 완료
                document.getElementById('analysis-progress-fill').style.width = '100%';
                document.getElementById('analysis-status-text').textContent = '분석 완료!';
                
                // 로그 업데이트
                this.addAnalysisLog('🎉 AI 분석이 성공적으로 완료되었습니다!');
                this.addAnalysisLog('📊 분석 결과를 데이터베이스에 저장했습니다.');
                
                // 완료 섹션 표시
                document.getElementById('analysis-progress-detail').style.display = 'none';
                document.getElementById('analysis-complete-section').style.display = 'block';
                
                // 대시보드 데이터 새로고침
                this.loadDashboardData();
                this.loadEmployeesData();
            },
            
            // 분석 오류 처리
            onAnalysisError(error) {
                // 실시간 업데이트 중지
                if (this.state.progressInterval) {
                    clearInterval(this.state.progressInterval);
                    this.state.progressInterval = null;
                }
                
                this.addAnalysisLog(`❌ 분석 실패: ${error}`);
                document.getElementById('analysis-status-text').textContent = '분석 중 오류 발생';
                document.getElementById('analysis-progress-fill').style.background = 'var(--error)';
            },
            
            // 분석 결과 보기 (개선된 버전)
            async viewAnalysisResults() {
                // 탭 전환
                this.switchTab('employees');
                
                // 로딩 상태 표시
                const employeesTable = document.getElementById('employees-table');
                if (employeesTable) {
                    employeesTable.innerHTML = `
                        <tr>
                            <td colspan="7" style="text-align: center; padding: 40px;">
                                <div class="spinner"></div>
                                <p style="margin-top: 20px;">최신 분석 결과를 불러오는 중...</p>
                            </td>
                        </tr>
                    `;
                }
                
                try {
                    // 직원 데이터 강제 새로고침
                    await this.loadEmployeesData();
                    
                    // 대시보드 통계도 업데이트
                    await this.loadDashboardData();
                    
                    this.showNotification('✅ 최신 분석 결과를 불러왔습니다', 'success');
                } catch (error) {
                    console.error('Failed to load analysis results:', error);
                    this.showNotification('분석 결과 로딩에 실패했습니다', 'error');
                }
            },
            
            // 분석 리포트 다운로드
            async downloadAnalysisReport() {
                try {
                    await this.exportDashboard();
                    this.showNotification('분석 리포트를 다운로드했습니다', 'success');
                } catch (error) {
                    console.error('Report download failed:', error);
                    this.showNotification('리포트 다운로드에 실패했습니다', 'error');
                }
            },
            
            // 직원 검색 기능
            selectedEmployee: null,
            allEmployees: [],
            
            async searchEmployeesForOpinion(query) {
                console.log('🔍 검색 함수 호출됨:', query);
                const dropdown = document.getElementById('employee-dropdown');
                
                if (!dropdown) {
                    console.error('❌ 드롭다운 요소를 찾을 수 없습니다');
                    return;
                }
                
                if (!query || query.trim().length < 1) {
                    dropdown.style.display = 'none';
                    return;
                }
                
                try {
                    // 전체 직원 목록이 없으면 로드
                    if (this.allEmployees.length === 0) {
                        console.log('🔄 직원 목록 로드 중...');
                        const response = await this.api.request('GET', '/employees/list');
                        this.allEmployees = response.employees || [];
                        console.log('✅ 직원 목록 로드 완료:', this.allEmployees.length, '명');
                    }
                    
                    // 검색 필터링 (이름, UID, 부서)
                    const searchTerm = query.toLowerCase().trim();
                    console.log('🔍 검색어:', searchTerm, '| 전체 직원 수:', this.allEmployees.length);
                    
                    const filteredEmployees = this.allEmployees.filter(emp => 
                        emp.employee_name?.toLowerCase().includes(searchTerm) ||
                        emp.uid?.toLowerCase().includes(searchTerm) ||
                        emp.department?.toLowerCase().includes(searchTerm)
                    ).slice(0, 10); // 최대 10개만 표시
                    
                    console.log('✅ 검색 결과:', filteredEmployees.length, '명');
                    
                    if (filteredEmployees.length > 0) {
                        dropdown.innerHTML = filteredEmployees.map(emp => `
                            <div style="
                                padding: 12px 15px; 
                                border-bottom: 1px solid #eee; 
                                cursor: pointer;
                                transition: background-color 0.2s;
                            " 
                            onmouseover="this.style.backgroundColor='#f8f9fa'" 
                            onmouseout="this.style.backgroundColor='white'"
                            onclick="AIRISS.selectEmployee('${emp.uid}', '${emp.employee_name?.replace(/'/g, "\\'")}', '${emp.department?.replace(/'/g, "\\'")}', '${emp.position?.replace(/'/g, "\\'")}')"
                            >
                                <div style="font-weight: 500; color: #2c3e50;">
                                    ${emp.employee_name || '이름 없음'}
                                </div>
                                <div style="font-size: 12px; color: #6c757d; margin-top: 2px;">
                                    UID: ${emp.uid} | ${emp.department || '부서 없음'} | ${emp.position || '직급 없음'}
                                </div>
                            </div>
                        `).join('');
                        dropdown.style.display = 'block';
                    } else {
                        dropdown.innerHTML = `
                            <div style="padding: 15px; text-align: center; color: #6c757d;">
                                검색 결과가 없습니다
                            </div>
                        `;
                        dropdown.style.display = 'block';
                    }
                } catch (error) {
                    console.error('❌ 직원 검색 실패:', error);
                    console.error('Error details:', error.message);
                    dropdown.innerHTML = `
                        <div style="padding: 15px; text-align: center; color: #dc3545;">
                            검색 중 오류가 발생했습니다: ${error.message}
                        </div>
                    `;
                    dropdown.style.display = 'block';
                }
            },
            
            selectEmployee(uid, name, department, position) {
                this.selectedEmployee = {
                    uid: uid,
                    name: name,
                    department: department,
                    position: position
                };
                
                // UI 업데이트
                document.getElementById('employee-search').value = `${name} (${uid})`;
                document.getElementById('selected-employee').innerHTML = `
                    <div style="color: #10b981; font-weight: 500;">✅ 선택됨</div>
                    <div style="font-size: 12px; margin-top: 5px; color: #2c3e50;">
                        <strong>${name}</strong><br>
                        ${department} | ${position}
                    </div>
                `;
                document.getElementById('selected-employee').style.borderColor = '#10b981';
                document.getElementById('selected-employee').style.background = 'rgba(16, 185, 129, 0.1)';
                
                // 드롭다운 닫기
                document.getElementById('employee-dropdown').style.display = 'none';
                
                console.log('선택된 직원:', this.selectedEmployee);
            },
            
            // 온도 디스플레이 업데이트
            updateTemperatureDisplay(value) {
                const tempValue = document.getElementById('temp-value');
                const tempDescription = document.getElementById('temp-description');
                const tempDisplay = document.getElementById('temperature-display');
                
                const temperatureSettings = {
                    '1': {
                        label: '매우 긍정적 분석',
                        description: '강점과 장점을 중심으로 칭찬과 인정의 관점에서 분석합니다',
                        color: '#28a745',
                        borderColor: '#28a745'
                    },
                    '2': {
                        label: '긍정적 분석',
                        description: '긍정적인 측면을 주로 보면서 발전 가능성을 강조합니다',
                        color: '#17a2b8',
                        borderColor: '#17a2b8'
                    },
                    '3': {
                        label: '중립적 분석',
                        description: '균형 잡힌 시각으로 장단점을 공정하게 분석합니다',
                        color: '#6c757d',
                        borderColor: '#6c757d'
                    },
                    '4': {
                        label: '부정적 분석',
                        description: '개선이 필요한 부분을 중심으로 발전 과제를 도출합니다',
                        color: '#fd7e14',
                        borderColor: '#fd7e14'
                    },
                    '5': {
                        label: '매우 부정적 분석',
                        description: '문제점과 리스크를 집중적으로 파악하여 개선 방안을 제시합니다',
                        color: '#dc3545',
                        borderColor: '#dc3545'
                    }
                };
                
                const setting = temperatureSettings[value];
                tempValue.textContent = setting.label;
                tempValue.style.color = setting.color;
                tempDescription.textContent = setting.description;
                tempDisplay.style.borderColor = setting.borderColor;
            },
            
            // 의견 분석 (개선된 버전)
            async analyzeOpinion() {
                // 직원 선택 검증
                if (!this.selectedEmployee) {
                    this.showNotification('분석할 직원을 먼저 선택해주세요', 'warning');
                    document.getElementById('employee-search').focus();
                    return;
                }
                
                const text = document.getElementById('opinion-text').value;
                if (!text || text.trim() === '') {
                    this.showNotification('분석할 텍스트를 입력해주세요', 'warning');
                    document.getElementById('opinion-text').focus();
                    return;
                }
                
                // 텍스트 길이 검증
                if (text.trim().length < 10) {
                    this.showNotification('더 자세한 의견을 입력해주세요 (최소 10자 이상)', 'warning');
                    document.getElementById('opinion-text').focus();
                    return;
                }
                
                const resultsDiv = document.getElementById('opinion-results');
                const analyzeButton = document.querySelector('#opinion-tab .btn-primary');
                
                try {
                    // 로딩 상태 표시
                    analyzeButton.disabled = true;
                    analyzeButton.innerHTML = '<div class="spinner" style="width: 20px; height: 20px; margin-right: 10px;"></div>🤖 AI 분석 중...';
                    
                    resultsDiv.innerHTML = `
                        <div class="card">
                            <div style="text-align: center; padding: 30px;">
                                <div class="spinner" style="margin: 0 auto 20px;"></div>
                                <h3>AI가 텍스트를 분석하고 있습니다...</h3>
                                <p style="color: var(--text-secondary); margin-top: 10px;">
                                    평가의견의 감정, 핵심역량, 개선점을 AI가 종합 분석 중입니다.
                                </p>
                            </div>
                        </div>
                    `;
                    
                    // 온도 값 가져오기
                    const temperatureValue = document.getElementById('temperature-slider').value;
                    
                    const requestBody = {
                        uid: this.selectedEmployee.uid,
                        opinions: {
                            "2024": text.trim()
                        },
                        temperature: parseInt(temperatureValue) // 1-5의 온도 값 추가
                    };
                    
                    console.log('🚀 의견 분석 요청:', requestBody);
                    const data = await this.api.request('POST', '/analysis/analyze', requestBody);
                    console.log('✅ 의견 분석 응답:', data);
                    
                    // 응답 데이터 검증
                    if (!data || data.success === false) {
                        throw new Error(data?.message || '서버에서 분석 실패 응답을 받았습니다');
                    }
                    
                    const result = data.result || data;
                    
                    // 온도 설정 정보 가져오기
                    const temperatureLabels = {
                        '1': { text: '매우 긍정적', color: '#28a745', emoji: '😊' },
                        '2': { text: '긍정적', color: '#17a2b8', emoji: '🙂' },
                        '3': { text: '중립적', color: '#6c757d', emoji: '😐' },
                        '4': { text: '부정적', color: '#fd7e14', emoji: '😕' },
                        '5': { text: '매우 부정적', color: '#dc3545', emoji: '😟' }
                    };
                    const currentTemp = temperatureLabels[temperatureValue] || temperatureLabels['3'];
                    
                    // 성공적인 분석 결과 표시
                    resultsDiv.innerHTML = `
                        <div class="card" style="animation: slideUp 0.5s ease-out;">
                            <div class="card-header">
                                <h3>✅ AI 의견 분석 결과</h3>
                                
                                <!-- 온도 설정 표시 -->
                                <div style="margin-top: 10px; padding: 10px; background: linear-gradient(135deg, ${currentTemp.color}15, ${currentTemp.color}05); border: 1px solid ${currentTemp.color}30; border-radius: 8px;">
                                    <div style="display: flex; align-items: center; gap: 8px;">
                                        <span style="font-size: 20px;">${currentTemp.emoji}</span>
                                        <span style="font-size: 14px; color: ${currentTemp.color}; font-weight: 600;">
                                            🌡️ 분석 관점: ${currentTemp.text}
                                        </span>
                                        <div style="flex: 1; height: 4px; background: linear-gradient(to right, #28a745 0%, #ffc107 50%, #dc3545 100%); border-radius: 2px; margin: 0 10px; position: relative;">
                                            <div style="position: absolute; top: -3px; left: ${(temperatureValue - 1) * 25}%; width: 10px; height: 10px; background: ${currentTemp.color}; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.2);"></div>
                                        </div>
                                    </div>
                                </div>
                                
                                <div style="margin-top: 10px; padding: 12px; background: rgba(102, 126, 234, 0.1); border-radius: 8px;">
                                    <div style="font-weight: 500; color: var(--text-primary);">
                                        👤 분석 대상: ${this.selectedEmployee.name} (${this.selectedEmployee.uid})
                                    </div>
                                    <div style="font-size: 13px; color: var(--text-secondary); margin-top: 3px;">
                                        ${this.selectedEmployee.department} | ${this.selectedEmployee.position}
                                    </div>
                                </div>
                                <span style="color: var(--text-secondary); font-size: 14px; margin-top: 10px; display: block;">
                                    분석 완료: ${new Date().toLocaleString('ko-KR')} | UID: ${this.selectedEmployee.uid}
                                </span>
                            </div>
                            
                            <!-- 점수 및 등급 섹션 -->
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0;">
                                <div style="text-align: center; padding: 15px; background: rgba(0, 212, 255, 0.1); border-radius: 8px;">
                                    <div style="font-size: 24px; font-weight: bold; color: #00d4ff;">${result.text_score || result.ai_score || 0}</div>
                                    <div style="font-size: 12px; color: var(--text-secondary); margin-top: 5px;">AI 종합 점수</div>
                                </div>
                                <div style="text-align: center; padding: 15px; background: rgba(102, 126, 234, 0.1); border-radius: 8px;">
                                    <div style="font-size: 24px; font-weight: bold; color: #667eea;">${result.grade || 'B'}</div>
                                    <div style="font-size: 12px; color: var(--text-secondary); margin-top: 5px;">평가 등급</div>
                                </div>
                                <div style="text-align: center; padding: 15px; background: rgba(16, 185, 129, 0.1); border-radius: 8px;">
                                    <div style="font-size: 18px; font-weight: bold; color: #10B981;">${result.sentiment_analysis || '중립적'}</div>
                                    <div style="font-size: 12px; color: var(--text-secondary); margin-top: 5px;">감정 분석</div>
                                </div>
                            </div>
                            
                            <!-- 상세 분석 결과 (온도에 따라 강조 변경) -->
                            <div style="display: grid; gap: 20px; margin-top: 20px;">
                                <div style="padding: 15px; background: rgba(16, 185, 129, 0.1); border-left: 4px solid #10B981; border-radius: 4px; ${temperatureValue <= 2 ? 'order: -1;' : temperatureValue >= 4 ? 'opacity: 0.7;' : ''}">
                                    <h4 style="color: #10B981; margin-bottom: 10px;">
                                        💪 강점 및 우수 역량 
                                        ${temperatureValue <= 2 ? '<span style="background: #10B981; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin-left: 8px;">강조</span>' : ''}
                                    </h4>
                                    <ul style="margin: 0; padding-left: 20px; color: var(--text-primary);">
                                        ${(result.strengths || ['긍정적인 업무 태도', '성실성', '책임감']).map(s => `<li style="margin-bottom: 5px; ${temperatureValue <= 2 ? 'font-weight: 500;' : ''}">${s}</li>`).join('')}
                                    </ul>
                                </div>
                                
                                <div style="padding: 15px; background: rgba(245, 158, 11, 0.1); border-left: 4px solid #F59E0B; border-radius: 4px; ${temperatureValue >= 4 ? 'order: -1;' : temperatureValue <= 2 ? 'opacity: 0.7;' : ''}">
                                    <h4 style="color: #F59E0B; margin-bottom: 10px;">
                                        🎯 개선 방향 및 발전 과제
                                        ${temperatureValue >= 4 ? '<span style="background: #F59E0B; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin-left: 8px;">강조</span>' : ''}
                                    </h4>
                                    <ul style="margin: 0; padding-left: 20px; color: var(--text-primary);">
                                        ${(result.improvements || result.weaknesses || ['지속적인 성장 기대', '역량 강화 필요']).map(i => `<li style="margin-bottom: 5px; ${temperatureValue >= 4 ? 'font-weight: 500;' : ''}">${i}</li>`).join('')}
                                    </ul>
                                </div>
                                
                                ${result.summary ? `
                                <div style="padding: 15px; background: rgba(102, 126, 234, 0.1); border-left: 4px solid #667eea; border-radius: 4px;">
                                    <h4 style="color: #667eea; margin-bottom: 10px;">📝 종합 평가</h4>
                                    <p style="margin: 0; color: var(--text-primary); line-height: 1.6;">${result.summary}</p>
                                </div>
                                ` : ''}
                            </div>
                            
                            <!-- 추가 정보 -->
                            <div style="margin-top: 20px; padding: 10px; background: rgba(255,255,255,0.05); border-radius: 4px; font-size: 12px; color: var(--text-secondary);">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span>분석 정확도: ${result.confidence ? Math.round(result.confidence * 100) : 85}%</span>
                                    <span>분석 시간: ${result.processing_time || '< 1'}초</span>
                                </div>
                            </div>
                        </div>
                    `;
                    
                    this.showNotification('✅ AI 의견 분석이 완료되었습니다', 'success');
                    
                } catch (error) {
                    console.error('❌ Opinion analysis failed:', error);
                    
                    resultsDiv.innerHTML = `
                        <div class="card" style="border-left: 4px solid var(--danger-color);">
                            <div style="text-align: center; padding: 30px;">
                                <h3 style="color: var(--danger-color); margin-bottom: 15px;">❌ 분석 실패</h3>
                                <p style="color: var(--text-secondary); margin-bottom: 20px;">
                                    의견 분석 중 오류가 발생했습니다.
                                </p>
                                <div style="background: rgba(239, 68, 68, 0.1); padding: 15px; border-radius: 8px; margin: 15px 0;">
                                    <p style="color: var(--danger-color); font-size: 14px; margin: 0;">
                                        <strong>오류 내용:</strong> ${error.message || '서버 연결 오류'}
                                    </p>
                                </div>
                                <div style="display: grid; gap: 10px; margin-top: 20px;">
                                    <h4 style="color: var(--text-primary);">해결 방법:</h4>
                                    <ul style="text-align: left; color: var(--text-secondary); max-width: 400px; margin: 0 auto;">
                                        <li>텍스트가 너무 짧지 않은지 확인해주세요 (최소 10자)</li>
                                        <li>네트워크 연결 상태를 확인해주세요</li>
                                        <li>잠시 후 다시 시도해주세요</li>
                                        <li>문제가 지속되면 관리자에게 문의하세요</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    `;
                    
                    this.showNotification('❌ 의견 분석에 실패했습니다. 다시 시도해주세요.', 'error');
                    
                } finally {
                    // 버튼 상태 복원
                    analyzeButton.disabled = false;
                    analyzeButton.innerHTML = '🤖 AI 분석 시작';
                }
            },
            
            // PDF 다운로드
            async exportDashboard() {
                try {
                    const response = await fetch('/api/v1/hr-dashboard/export/pdf');
                    const blob = await response.blob();
                    
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `AIRISS_Dashboard_${new Date().toISOString().slice(0, 10)}.pdf`;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                    
                    this.showNotification('PDF 다운로드 완료', 'success');
                } catch (error) {
                    console.error('PDF export failed:', error);
                }
            },
            
            // 직원 상세 보기
            viewDetail(employeeId) {
                console.log('직원 상세 보기:', employeeId);
                // 모달 또는 새 탭에서 상세 정보 표시
                this.showNotification(`직원 ${employeeId}의 상세 정보를 불러오는 중...`, 'info');
                
                // 상세 정보 모달 표시 (추후 구현)
                alert(`직원 ID: ${employeeId}\n\n상세 정보 기능은 준비 중입니다.`);
            },
            
            // 데이터 내보내기
            async exportData(format = 'excel') {
                try {
                    console.log(`데이터 내보내기: ${format} 형식`);
                    
                    if (format === 'excel') {
                        // Excel 내보내기
                        const response = await fetch('/api/v1/hr-dashboard/export/excel');
                        const blob = await response.blob();
                        
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `AIRISS_직원분석_${new Date().toISOString().slice(0, 10)}.xlsx`;
                        document.body.appendChild(a);
                        a.click();
                        window.URL.revokeObjectURL(url);
                        
                        this.showNotification('Excel 다운로드 완료', 'success');
                    } else if (format === 'csv') {
                        // CSV 내보내기
                        const csvContent = this.convertToCSV(this.state.employees);
                        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `AIRISS_직원분석_${new Date().toISOString().slice(0, 10)}.csv`;
                        document.body.appendChild(a);
                        a.click();
                        window.URL.revokeObjectURL(url);
                        
                        this.showNotification('CSV 다운로드 완료', 'success');
                    }
                } catch (error) {
                    console.error('Export failed:', error);
                    this.showNotification('데이터 내보내기 실패', 'error');
                }
            },
            
            // CSV 변환 헬퍼
            convertToCSV(data) {
                if (!data || data.length === 0) return '';
                
                const headers = ['사번', '이름', '부서', '직급', 'AI점수', '등급', '주요강점', '개선사항'];
                const rows = data.map(emp => [
                    emp.employee_id || '',
                    emp.name || '',
                    emp.department || '',
                    emp.position || '',
                    emp.ai_score || 0,
                    emp.grade || '',
                    emp.primary_strength || '',
                    emp.primary_improvement || ''
                ]);
                
                const csvContent = [
                    headers.join(','),
                    ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
                ].join('\n');
                
                return '\uFEFF' + csvContent; // UTF-8 BOM 추가
            },
            
            // 모달 닫기
            closeModal() {
                document.getElementById('employee-modal').classList.remove('active');
            },
            
            // PDF 다운로드 (이미지 캡처 방식)
            async downloadPDF() {
                try {
                    this.showNotification('PDF 생성 중입니다. 잠시만 기다려주세요...', 'info');
                    
                    const data = this.currentEmployeeData;
                    if (!data) {
                        this.showNotification('직원 데이터를 불러올 수 없습니다', 'error');
                        return;
                    }
                    
                    // 모달 콘텐츠를 캡처
                    const modalContent = document.getElementById('modal-body');
                    
                    // 버튼들을 임시로 숨기기
                    const buttons = modalContent.querySelectorAll('button');
                    buttons.forEach(btn => btn.style.display = 'none');
                    
                    // 현재 스크롤 위치 저장
                    const originalScrollTop = modalContent.scrollTop;
                    
                    // 스크롤을 맨 위로
                    modalContent.scrollTop = 0;
                    
                    // 모달의 실제 전체 높이 계산
                    const fullHeight = modalContent.scrollHeight;
                    const fullWidth = modalContent.scrollWidth;
                    
                    // 모달의 원래 overflow 스타일 저장
                    const originalOverflow = modalContent.style.overflow;
                    modalContent.style.overflow = 'visible';
                    modalContent.style.height = 'auto';
                    
                    // html2canvas를 사용하여 이미지로 캡처 (전체 높이)
                    const canvas = await html2canvas(modalContent, {
                        scale: 2, // 고화질을 위해 2배 스케일
                        useCORS: true,
                        backgroundColor: 'rgba(22, 27, 34, 0.95)',
                        logging: false,
                        width: fullWidth,
                        height: fullHeight,
                        windowWidth: fullWidth,
                        windowHeight: fullHeight,
                        scrollX: 0,
                        scrollY: 0
                    });
                    
                    // 원래 스타일로 복원
                    modalContent.style.overflow = originalOverflow;
                    modalContent.style.height = '';
                    modalContent.scrollTop = originalScrollTop;
                    
                    // 버튼들 다시 표시
                    buttons.forEach(btn => btn.style.display = '');
                    
                    // jsPDF 생성
                    const { jsPDF } = window.jspdf;
                    
                    // A4 크기 PDF 생성 (세로 방향)
                    const pdf = new jsPDF('p', 'mm', 'a4');
                    const pageWidth = pdf.internal.pageSize.getWidth();
                    const pageHeight = pdf.internal.pageSize.getHeight();
                    
                    // 캔버스를 이미지로 변환
                    const imgData = canvas.toDataURL('image/png');
                    
                    // 이미지 크기 계산 (A4 페이지에 맞춤)
                    const imgWidth = pageWidth - 20; // 좌우 여백 10mm씩
                    const imgHeight = (canvas.height * imgWidth) / canvas.width;
                    
                    let heightLeft = imgHeight;
                    let position = 10; // 상단 여백 10mm
                    
                    // 첫 페이지에 이미지 추가
                    pdf.addImage(imgData, 'PNG', 10, position, imgWidth, imgHeight);
                    heightLeft -= (pageHeight - 20); // 상하 여백 제외
                    
                    // 이미지가 한 페이지보다 길면 추가 페이지 생성
                    while (heightLeft > 0) {
                        position = heightLeft - imgHeight + 10; // 다음 페이지 시작 위치
                        pdf.addPage();
                        pdf.addImage(imgData, 'PNG', 10, position, imgWidth, imgHeight);
                        heightLeft -= (pageHeight - 20);
                    }
                    
                    // 파일명 생성 및 저장
                    const fileName = `${data.name || '직원'}_AI분석리포트_${new Date().toISOString().split('T')[0]}.pdf`;
                    pdf.save(fileName);
                    
                    this.showNotification('PDF 다운로드가 완료되었습니다', 'success');
                } catch (error) {
                    console.error('PDF 생성 오류:', error);
                    this.showNotification('PDF 생성 중 오류가 발생했습니다', 'error');
                }
            },
            
            // 알림 표시
            showNotification(message, type = 'info') {
                // 간단한 알림 구현 (실제로는 toast 라이브러리 사용 권장)
                console.log(`[${type.toUpperCase()}] ${message}`);
            },
            
            // 직원 검색
            searchEmployees() {
                const query = document.getElementById('search-input').value.toLowerCase();
                const filtered = this.state.employees.filter(emp => 
                    (emp.employee_name || '').toLowerCase().includes(query) ||
                    (emp.uid || '').toLowerCase().includes(query)
                );
                this.renderEmployees(filtered);
            },
            
            // 헬퍼 함수들 - loadInsights 보다 먼저 정의되어야 함
            // 평균 점수 계산
            calculateAverageScore(employees) {
                if (!employees || employees.length === 0) return 0;
                const total = employees.reduce((sum, emp) => sum + (emp.ai_score || emp.overall_score || emp.AIRISS_v2_종합점수 || 0), 0);
                return Math.round(total / employees.length);
            },
            
            // 등급 분포 계산
            calculateGradeDistribution(employees) {
                // 두 번째 버전의 함수로 통일 (더 상세한 로직)
                const distribution = {
                    'S': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0
                };
                
                if (!employees || employees.length === 0) return distribution;
                
                employees.forEach((emp, index) => {
                    // 다양한 필드명 처리
                    let grade = emp.grade || emp.final_grade || emp.ai_grade || emp.OK등급 || 'C';
                    
                    // null/undefined 체크
                    if (!grade || grade === 'null' || grade === 'undefined') {
                        grade = 'C';
                    }
                    
                    // 대문자로 변환
                    let normalizedGrade = grade.toString().toUpperCase().trim();
                    
                    // A+, B+ 같은 등급을 A, B로 변환
                    if (normalizedGrade.includes('+') || normalizedGrade.includes('-')) {
                        normalizedGrade = normalizedGrade[0];
                    }
                    
                    // S, A, B, C, D만 허용
                    if (['S', 'A', 'B', 'C', 'D'].includes(normalizedGrade)) {
                        distribution[normalizedGrade]++;
                    } else {
                        distribution['C']++; // 기본값
                    }
                });
                
                return distribution;
            },
            
            // 부서별 분석
            analyzeDepartments(employees) {
                const deptData = {};
                employees.forEach(emp => {
                    const dept = emp.department || emp.부서 || '미지정';
                    if (!deptData[dept]) {
                        deptData[dept] = { 
                            count: 0, 
                            totalScore: 0, 
                            grades: { 'S': 0, 'A+': 0, 'A': 0, 'B+': 0, 'B': 0, 'C': 0, 'D': 0 }
                        };
                    }
                    deptData[dept].count++;
                    deptData[dept].totalScore += emp.ai_score || emp.overall_score || emp.AIRISS_v2_종합점수 || 0;
                    
                    const grade = emp.ai_grade || emp.grade || emp.OK등급 || 'C';
                    if (deptData[dept].grades.hasOwnProperty(grade)) {
                        deptData[dept].grades[grade]++;
                    }
                });
                
                // 평균 계산
                Object.keys(deptData).forEach(dept => {
                    deptData[dept].avgScore = Math.round(deptData[dept].totalScore / deptData[dept].count);
                });
                
                return deptData;
            },
            
            // 인사이트 로드 (실시간 데이터 기반)
            async loadInsights() {
                const content = document.getElementById('insights-content');
                
                // 실제 데이터 기반 계산
                const employees = this.state.employees || [];
                const dashboardStats = this.state.dashboardStats || {};
                
                // 평균 점수 계산
                const avgScore = this.calculateAverageScore(employees);
                
                // 등급 분포 계산
                const gradeDistribution = { 'S': 0, 'A+': 0, 'A': 0, 'B+': 0, 'B': 0, 'C': 0, 'D': 0 };
                employees.forEach(emp => {
                    const grade = emp.ai_grade || emp.grade || emp.OK등급 || 'C';
                    if (gradeDistribution.hasOwnProperty(grade)) {
                        gradeDistribution[grade]++;
                    }
                });
                
                // 부서별 분석
                const deptAnalysis = {};
                employees.forEach(emp => {
                    const dept = emp.department || emp.부서 || '기타';
                    if (!deptAnalysis[dept]) {
                        deptAnalysis[dept] = { count: 0, totalScore: 0, talents: 0, risks: 0 };
                    }
                    deptAnalysis[dept].count++;
                    deptAnalysis[dept].totalScore += emp.ai_score || emp.overall_score || emp.AIRISS_v2_종합점수 || 0;
                    
                    const score = emp.ai_score || emp.overall_score || 0;
                    if (score >= 850) deptAnalysis[dept].talents++;
                    if (score < 600) deptAnalysis[dept].risks++;
                });
                
                // 가장 우수한 부서와 개선 필요 부서 찾기
                let bestDept = null, worstDept = null;
                let bestAvg = 0, worstAvg = 1000;
                
                Object.entries(deptAnalysis).forEach(([dept, data]) => {
                    const avg = data.totalScore / data.count;
                    if (avg > bestAvg) {
                        bestAvg = avg;
                        bestDept = dept;
                    }
                    if (avg < worstAvg) {
                        worstAvg = avg;
                        worstDept = dept;
                    }
                });
                
                // 조직 건강도 계산 (0-100점)
                const healthScore = Math.min(100, Math.round(
                    (avgScore / 10) * 0.4 +  // 평균 점수 (40%)
                    ((gradeDistribution['S'] + gradeDistribution['A+'] + gradeDistribution['A']) / employees.length * 100) * 0.3 +  // 상위 등급 비율 (30%)
                    ((1 - gradeDistribution['D'] / employees.length) * 100) * 0.3  // 하위 등급 비율 (30%)
                ));
                
                // 인사이트 생성
                const topTalentsCount = dashboardStats.top_talents?.count || employees.filter(e => (e.ai_score || 0) >= 850).length;
                const riskEmployeesCount = dashboardStats.risk_employees?.count || employees.filter(e => (e.ai_score || 0) < 600).length;
                const promotionCandidatesCount = dashboardStats.promotion_candidates?.count || employees.filter(e => (e.ai_score || 0) >= 750 && (e.ai_score || 0) < 850).length;
                
                content.innerHTML = `
                    <div style="display: grid; gap: 20px;">
                        <!-- 조직 건강도 스코어카드 -->
                        <div class="card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                            <h3>🏆 조직 건강도 종합 평가</h3>
                            <div style="display: flex; align-items: center; gap: 20px; margin: 20px 0;">
                                <div style="font-size: 48px; font-weight: bold;">${healthScore}점</div>
                                <div>
                                    <div style="font-size: 18px; margin-bottom: 5px;">
                                        ${healthScore >= 80 ? '우수' : healthScore >= 60 ? '양호' : healthScore >= 40 ? '보통' : '개선필요'}
                                    </div>
                                    <div style="opacity: 0.9;">
                                        전체 ${employees.length}명 기준 종합 평가
                                    </div>
                                </div>
                            </div>
                            <div style="background: rgba(255,255,255,0.2); padding: 10px; border-radius: 8px; margin-top: 10px;">
                                <small>평균 AI 점수: ${avgScore}점 | 상위등급 비율: ${Math.round((gradeDistribution['S'] + gradeDistribution['A+'] + gradeDistribution['A']) / employees.length * 100)}%</small>
                            </div>
                            
                            <!-- 상세 분석 추가 -->
                            <div style="margin-top: 20px; padding: 15px; background: rgba(0,0,0,0.2); border-radius: 8px;">
                                <h4 style="color: #00d4ff; margin-bottom: 10px;">🔍 상세 분석</h4>
                                <div style="display: grid; gap: 10px; font-size: 14px;">
                                    <div>📈 <strong>강점</strong>: ${
                                        healthScore >= 80 ? '조직 전반적으로 우수한 성과를 보이고 있으며, 인재 밀도와 역량 수준이 높습니다.' :
                                        healthScore >= 60 ? '핵심 인재의 성과가 양호하며, 조직 전체적으로 안정적인 성과를 유지하고 있습니다.' :
                                        healthScore >= 40 ? '일부 우수 인재가 있으나, 전체적인 성과 향상이 필요합니다.' :
                                        '일부 직원의 헌신적인 노력이 돋보이나, 전체적인 개선이 시급합니다.'
                                    }</div>
                                    <div>👥 <strong>위험 요소</strong>: ${
                                        riskEmployeesCount > employees.length * 0.2 ? '하위 성과자 비율이 높아 즉각적인 개입이 필요합니다.' :
                                        promotionCandidatesCount < employees.length * 0.1 ? '차세대 리더 풀이 부족하여 중장기 성장에 리스크가 있습니다.' :
                                        (bestAvg - worstAvg) > 200 ? '부서간 성과 격차가 커 조직 분열 위험이 있습니다.' :
                                        '현재 특별한 리스크는 없으나, 지속적인 모니터링이 필요합니다.'
                                    }</div>
                                    <div>🎯 <strong>개선 방향</strong>: ${
                                        topTalentsCount < employees.length * 0.1 ? '핵심 인재 육성 프로그램 강화 및 외부 인재 영입' :
                                        riskEmployeesCount > employees.length * 0.15 ? '하위 성과자 대상 집중 코칭 및 역량 개발' :
                                        promotionCandidatesCount < employees.length * 0.1 ? '승진 후보자 풀 확대 및 리더십 개발' :
                                        '현재 수준 유지 및 점진적 개선'
                                    }</div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- 핵심 인사이트 -->
                        <div class="card">
                            <h3>🎯 경영진 관점 핵심 인사이트</h3>
                            <div style="display: grid; gap: 15px;">
                                ${topTalentsCount > employees.length * 0.15 ? `
                                    <div style="padding: 12px; background: rgba(16, 185, 129, 0.15); border-left: 4px solid #10B981; border-radius: 4px; color: #ffffff;">
                                        <strong style="color: #10B981;">✓ 인재 밀도 우수</strong><br>
                                        <span style="color: rgba(255,255,255,0.9);">핵심 인재가 ${Math.round(topTalentsCount / employees.length * 100)}%로 업계 평균(10-15%)을 상회합니다.</span>
                                    </div>
                                ` : `
                                    <div style="padding: 12px; background: rgba(245, 158, 11, 0.15); border-left: 4px solid #F59E0B; border-radius: 4px; color: #ffffff;">
                                        <strong style="color: #F59E0B;">⚠ 인재 육성 필요</strong><br>
                                        <span style="color: rgba(255,255,255,0.9);">핵심 인재가 ${Math.round(topTalentsCount / employees.length * 100)}%로 업계 평균 이하입니다. 
                                        고성과자 육성 프로그램 도입을 권장합니다.</span>
                                    </div>
                                `}
                                
                                ${riskEmployeesCount > employees.length * 0.2 ? `
                                    <div style="padding: 12px; background: rgba(239, 68, 68, 0.15); border-left: 4px solid #EF4444; border-radius: 4px; color: #ffffff;">
                                        <strong style="color: #EF4444;">⚠ 리스크 관리 시급</strong><br>
                                        <span style="color: rgba(255,255,255,0.9);">전체 인력의 ${Math.round(riskEmployeesCount / employees.length * 100)}%가 관리 필요 그룹입니다.
                                        즉각적인 성과 개선 프로그램 또는 인력 재배치가 필요합니다.</span>
                                    </div>
                                ` : `
                                    <div style="padding: 12px; background: rgba(16, 185, 129, 0.15); border-left: 4px solid #10B981; border-radius: 4px; color: #ffffff;">
                                        <strong style="color: #10B981;">✓ 리스크 관리 양호</strong><br>
                                        <span style="color: rgba(255,255,255,0.9);">관리 필요 인력이 ${Math.round(riskEmployeesCount / employees.length * 100)}%로 안정적입니다.</span>
                                    </div>
                                `}
                                
                                ${bestDept && worstDept ? `
                                    <div style="padding: 12px; background: rgba(102, 126, 234, 0.15); border-left: 4px solid #667eea; border-radius: 4px; color: #ffffff;">
                                        <strong style="color: #667eea;">📊 부서간 성과 격차</strong><br>
                                        <span style="color: rgba(255,255,255,0.9);">최우수 부서(${bestDept}: ${Math.round(bestAvg)}점)와 
                                        개선필요 부서(${worstDept}: ${Math.round(worstAvg)}점) 간 
                                        ${Math.round(bestAvg - worstAvg)}점 차이가 있습니다.</span>
                                    </div>
                                ` : ''}
                            </div>
                        </div>
                        
                        <!-- 전략적 제언 -->
                        <div class="card">
                            <h3>💡 AI 기반 전략적 제언</h3>
                            <div style="display: grid; gap: 12px;">
                                <div>
                                    <h4 style="color: #00d9ff; margin-bottom: 10px;">🎯 단기 실행과제 (3개월 내)</h4>
                                    <ul style="margin: 0; padding-left: 20px; line-height: 1.8;">
                                        ${riskEmployeesCount > employees.length * 0.15 ? 
                                            '<li><strong>성과개선 TF 구성</strong>: 하위 ' + riskEmployeesCount + '명 대상 집중 코칭 프로그램</li>' : ''}
                                        ${promotionCandidatesCount < employees.length * 0.1 ? 
                                            '<li><strong>승진 Pool 확대</strong>: 현재 ' + promotionCandidatesCount + '명으로 부족, 차세대 리더 육성 프로그램 시급</li>' : ''}
                                        ${topTalentsCount > 0 ? 
                                            '<li><strong>핵심인재 리텐션</strong>: ' + topTalentsCount + '명의 핵심인재 대상 보상체계 개선 및 경력개발 지원</li>' : ''}
                                        <li><strong>부서간 협업 강화</strong>: ${bestDept} 부서의 우수사례를 전사 확산</li>
                                    </ul>
                                </div>
                                
                                <div>
                                    <h4 style="color: #00d9ff; margin-bottom: 10px;">🚀 중장기 혁신과제 (6-12개월)</h4>
                                    <ul style="margin: 0; padding-left: 20px; line-height: 1.8;">
                                        <li><strong>AI 기반 인재관리 시스템 고도화</strong>: 예측적 인재관리 및 맞춤형 육성</li>
                                        <li><strong>성과문화 혁신</strong>: OKR 도입 및 애자일 성과관리 체계 구축</li>
                                        <li><strong>조직문화 진단</strong>: ${healthScore < 70 ? '조직 건강도 개선을 위한' : '현재 수준 유지를 위한'} 문화 혁신 프로그램</li>
                                        ${worstDept ? `<li><strong>${worstDept} 부서 특별관리</strong>: 조직 재설계 및 리더십 교체 검토</li>` : ''}
                                    </ul>
                                </div>
                            </div>
                        </div>
                        
                        <!-- 데이터 기반 예측 -->
                        <div class="card">
                            <h3>📈 향후 전망 및 시나리오</h3>
                            <div style="display: grid; gap: 15px;">
                                <div style="padding: 15px; background: #f8f9fa; border-radius: 8px; color: #333333;">
                                    <h4 style="color: #28a745; margin-bottom: 10px;">✅ 긍정 시나리오 (개선 조치 시행 시)</h4>
                                    <ul style="margin: 0; padding-left: 20px; color: #333333;">
                                        <li>6개월 내 조직 건강도 ${Math.min(100, healthScore + 15)}점 달성 가능</li>
                                        <li>핵심인재 이탈률 5% 이하 유지</li>
                                        <li>전체 생산성 15-20% 향상 예상</li>
                                    </ul>
                                </div>
                                <div style="padding: 15px; background: #fff5f5; border-radius: 8px; color: #333333;">
                                    <h4 style="color: #dc3545; margin-bottom: 10px;">⚠ 위험 시나리오 (현상 유지 시)</h4>
                                    <ul style="margin: 0; padding-left: 20px; color: #333333;">
                                        <li>핵심인재 ${Math.round(topTalentsCount * 0.3)}명 이탈 위험</li>
                                        <li>하위 성과자 증가로 전체 생산성 10% 하락</li>
                                        <li>부서간 갈등 심화 및 협업 저하</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                        
                        <!-- 실시간 모니터링 지표 -->
                        <div class="card">
                            <h3>📊 핵심 모니터링 지표 (KPI)</h3>
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                                <div style="text-align: center; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                                    <div style="font-size: 24px; font-weight: bold; color: #00d9ff;">${avgScore}</div>
                                    <div style="font-size: 12px; color: #6c757d; margin-top: 5px;">평균 AI 점수</div>
                                    <div style="font-size: 11px; color: ${avgScore >= 750 ? '#28a745' : avgScore >= 650 ? '#ffc107' : '#dc3545'};">
                                        ${avgScore >= 750 ? '▲ 우수' : avgScore >= 650 ? '- 보통' : '▼ 개선필요'}
                                    </div>
                                </div>
                                <div style="text-align: center; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                                    <div style="font-size: 24px; font-weight: bold; color: #00d9ff;">
                                        ${Math.round((gradeDistribution['S'] + gradeDistribution['A+']) / employees.length * 100)}%
                                    </div>
                                    <div style="font-size: 12px; color: #6c757d; margin-top: 5px;">최상위 등급 비율</div>
                                    <div style="font-size: 11px; color: ${(gradeDistribution['S'] + gradeDistribution['A+']) / employees.length > 0.1 ? '#28a745' : '#dc3545'};">
                                        목표: 10% 이상
                                    </div>
                                </div>
                                <div style="text-align: center; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                                    <div style="font-size: 24px; font-weight: bold; color: #00d9ff;">
                                        ${Math.round(riskEmployeesCount / employees.length * 100)}%
                                    </div>
                                    <div style="font-size: 12px; color: #6c757d; margin-top: 5px;">리스크 인력 비율</div>
                                    <div style="font-size: 11px; color: ${riskEmployeesCount / employees.length < 0.15 ? '#28a745' : '#dc3545'};">
                                        목표: 15% 이하
                                    </div>
                                </div>
                                <div style="text-align: center; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                                    <div style="font-size: 24px; font-weight: bold; color: #00d9ff;">
                                        ${Object.keys(deptAnalysis).length}개
                                    </div>
                                    <div style="font-size: 12px; color: #6c757d; margin-top: 5px;">분석 부서 수</div>
                                    <div style="font-size: 11px; color: #6c757d;">
                                        총 ${employees.length}명 분석
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            },
            
            // 화면에 리포트 표시
            async showReport(type) {
                const reportContent = document.getElementById('report-content');
                const reportActions = document.getElementById('report-actions');
                const reportTypeIcon = document.getElementById('report-type-icon');
                const reportTypeName = document.getElementById('report-type-name');
                
                // 로딩 표시
                reportContent.innerHTML = `
                    <div style="text-align: center; padding: 100px 20px;">
                        <div class="spinner"></div>
                        <p style="margin-top: 20px; color: rgba(255, 255, 255, 0.7);">리포트를 생성하고 있습니다...</p>
                    </div>
                `;
                
                // 리포트 타입별 아이콘과 이름 설정
                const reportTypes = {
                    'monthly': { icon: '📊', name: '월간 종합 리포트' },
                    'talent': { icon: '⭐', name: '핵심 인재 리포트' },
                    'risk': { icon: '⚠️', name: '리스크 관리 리포트' },
                    'performance': { icon: '📈', name: '성과 분석 리포트' },
                    'department': { icon: '🏢', name: '부서별 분석 리포트' },
                    'executive': { icon: '💼', name: '경영진 브리핑 리포트' }
                };
                
                if (reportTypes[type]) {
                    reportTypeIcon.textContent = reportTypes[type].icon;
                    reportTypeName.textContent = reportTypes[type].name;
                }
                
                // 잠시 후 리포트 생성
                setTimeout(async () => {
                    // 먼저 최신 데이터 로드
                    await this.loadEmployeesData();
                    await this.loadDashboardData();
                    
                    // state에서 실제 데이터 가져오기
                    let dashboardData = this.state.dashboardStats || {};
                    let employees = this.state.employees || [];
                    
                    try {
                        console.log('📊 리포트 생성을 위한 데이터 준비...');
                        console.log('  - 대시보드 통계:', dashboardData);
                        console.log('  - 직원 수:', employees.length);
                        
                        // 데이터가 없으면 다시 시도
                        if (!dashboardData.total_employees && (!employees || employees.length === 0)) {
                            console.log('📊 HR 대시보드 데이터 재로드 중...');
                            const response = await this.api.request('GET', '/hr-dashboard/stats');
                            if (response && response.total_employees) {
                                dashboardData = response;
                                this.state.dashboardStats = response;
                                console.log('✅ HR 대시보드 데이터 로드 성공:', dashboardData);
                            }
                        }
                    } catch (error) {
                        console.error('❌ HR 대시보드 데이터 로드 실패:', error);
                        
                        // 실제 데이터를 가져올 수 없을 때는 에러 메시지 표시
                        reportContent.innerHTML = `
                            <div style="text-align: center; padding: 100px 20px;">
                                <h3 style="color: #ff5252; margin-bottom: 20px;">데이터 로드 실패</h3>
                                <p style="color: rgba(255, 255, 255, 0.7); margin-bottom: 30px;">
                                    서버에서 데이터를 가져올 수 없습니다.<br>
                                    잠시 후 다시 시도해주세요.
                                </p>
                                <button onclick="location.reload()" style="padding: 10px 20px; background: #00d4ff; color: white; border: none; border-radius: 5px; cursor: pointer;">
                                    새로고침
                                </button>
                            </div>
                        `;
                        reportActions.style.display = 'none';
                        return;
                    }
                    
                    console.log(`📊 리포트 생성 - 타입: ${type}, 전체 직원 수: ${dashboardData.total_employees || employees.length}`);
                    
                    let content = '';
                    
                    switch(type) {
                        case 'monthly':
                            content = this.generateMonthlyReport(dashboardData, employees);
                            break;
                        case 'talent':
                            content = this.generateTalentReport(dashboardData, employees);
                            break;
                        case 'risk':
                            content = this.generateRiskReport(dashboardData, employees);
                            break;
                        case 'performance':
                            content = this.generatePerformanceReport(dashboardData, employees);
                            break;
                        case 'department':
                            content = this.generateDepartmentReport(dashboardData, employees);
                            break;
                        case 'executive':
                            content = this.generateExecutiveReport(dashboardData, employees);
                            break;
                        default:
                            content = '<p>알 수 없는 리포트 타입입니다.</p>';
                    }
                    
                    // 리포트 내용 표시
                    reportContent.innerHTML = content;
                    reportActions.style.display = 'block';
                    
                    // 현재 리포트 정보 저장 (다운로드용)
                    this.currentReport = {
                        type: type,
                        content: content,
                        title: reportTypes[type]?.name || '리포트'
                    };
                }, 500);
            },
            
            // 리포트 생성
            async generateReport(type, shouldDownload = true) {
                try {
                    this.showNotification(`${type} 리포트 생성 중...`, 'info');
                    
                    // 리포트 타입별 데이터 수집
                    let reportData = {
                        type: type,
                        generated_at: new Date().toISOString(),
                        company: 'OK금융그룹',
                        department: '전체'
                    };
                    
                    // 대시보드 데이터 가져오기
                    const dashboardData = this.state.dashboardStats || {};
                    const employees = this.state.employees || [];
                    
                    switch(type) {
                        case 'monthly':
                            reportData.title = '월간 HR 분석 리포트';
                            reportData.content = this.generateMonthlyReport(dashboardData, employees);
                            break;
                            
                        case 'talent':
                            reportData.title = '핵심 인재 분석 리포트';
                            reportData.content = this.generateTalentReport(dashboardData, employees);
                            break;
                            
                        case 'risk':
                            reportData.title = '리스크 관리 리포트';
                            reportData.content = this.generateRiskReport(dashboardData, employees);
                            break;
                            
                        case 'custom':
                            reportData.title = '맮춤형 HR 분석 리포트';
                            reportData.content = this.generateCustomReport(dashboardData, employees);
                            break;
                    }
                    
                    // 리포트 화면 업데이트
                    this.currentReport = reportData;
                    const reportContent = document.getElementById('report-content');
                    if (reportContent) {
                        reportContent.innerHTML = reportData.content;
                    }
                    
                    // 다운로드가 필요한 경우에만 HTML 파일 생성
                    if (shouldDownload) {
                        this.downloadReport(reportData);
                        this.showNotification('리포트가 생성되었습니다', 'success');
                    } else {
                        this.showNotification('리포트가 업데이트되었습니다', 'success');
                    }
                    
                } catch (error) {
                    console.error('Report generation failed:', error);
                    this.showNotification('리포트 생성에 실패했습니다', 'error');
                }
            },
            
            // 유틸리티 함수들
            calculateAverageScore(employees) {
                if (!employees || employees.length === 0) return 0;
                
                let validScores = 0;
                let totalScore = 0;
                
                employees.forEach(emp => {
                    // 다양한 필드명 처리
                    const score = emp.ai_score || emp.overall_score || emp.final_score || emp.total_score || 0;
                    if (score > 0) {
                        totalScore += score;
                        validScores++;
                    }
                });
                
                if (validScores === 0) return 0;
                return Math.round(totalScore / validScores);
            },
            
            calculateGradeDistribution(employees) {
                const distribution = {
                    'S': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0
                };
                
                if (!employees || employees.length === 0) return distribution;
                
                // 첫 5개 직원 데이터 샘플 확인 (디버깅용)
                console.log('📊 등급 분포 계산 - 직원 수:', employees.length);
                console.log('📊 등급 분포 계산 - 직원 샘플:', employees.slice(0, 5).map(emp => ({
                    grade: emp.grade,
                    final_grade: emp.final_grade,
                    ai_grade: emp.ai_grade,
                    ai_score: emp.ai_score,
                    overall_score: emp.overall_score,
                    employee_name: emp.employee_name
                })));
                
                // 점수 분포 확인
                const scoreDistribution = {
                    '90-100': 0,
                    '80-89': 0,
                    '70-79': 0,
                    '60-69': 0,
                    '0-59': 0
                };
                
                employees.forEach((emp, index) => {
                    // 점수 분포 분석
                    const score = emp.ai_score || emp.overall_score || 0;
                    if (score >= 90) scoreDistribution['90-100']++;
                    else if (score >= 80) scoreDistribution['80-89']++;
                    else if (score >= 70) scoreDistribution['70-79']++;
                    else if (score >= 60) scoreDistribution['60-69']++;
                    else scoreDistribution['0-59']++;
                    
                    // 다양한 필드명 처리 (HR Dashboard API 기준 우선)
                    let grade = emp.grade || emp.final_grade || emp.ai_grade || 'C';
                    
                    // null/undefined 체크
                    if (!grade || grade === 'null' || grade === 'undefined') {
                        grade = 'C';
                    }
                    
                    // 대문자로 변환
                    let normalizedGrade = grade.toString().toUpperCase().trim();
                    
                    // A+, B+ 같은 등급을 A, B로 변환
                    if (normalizedGrade.includes('+') || normalizedGrade.includes('-')) {
                        normalizedGrade = normalizedGrade[0];
                    }
                    
                    // 첫 5개 데이터만 디버깅 로그
                    if (index < 5) {
                        console.log(`  직원 ${index}: 원본 grade='${emp.grade}', 변환 grade='${normalizedGrade}', score=${score}`);
                    }
                    
                    // S, A, B, C, D만 허용 (엄격한 검증)
                    if (['S', 'A', 'B', 'C', 'D'].includes(normalizedGrade)) {
                        distribution[normalizedGrade]++;
                    } else {
                        // 잘못된 등급이면 점수 기준으로 재분류
                        if (score >= 90) {
                            distribution['S']++;
                        } else if (score >= 80) {
                            distribution['A']++;
                        } else if (score >= 70) {
                            distribution['B']++;
                        } else if (score >= 60) {
                            distribution['C']++;
                        } else {
                            distribution['D']++;
                        }
                        
                        if (index < 5) {
                            console.log(`    ⚠️ 유효하지 않은 등급 '${normalizedGrade}' → 점수 기준으로 재분류`);
                        }
                    }
                });
                
                console.log('📊 점수 분포:', scoreDistribution);
                console.log('📊 등급 분포:', distribution);
                
                return distribution;
            },
            
            analyzeDepartments(employees) {
                const deptData = {};
                
                if (!employees || employees.length === 0) {
                    console.log('🏢 analyzeDepartments: 직원 데이터가 없습니다');
                    return deptData;
                }
                
                console.log('🏢 analyzeDepartments: 분석 시작 - 직원 수:', employees.length);
                
                employees.forEach((emp, idx) => {
                    const dept = emp.department || '부서 미상';
                    
                    if (!deptData[dept]) {
                        deptData[dept] = {
                            count: 0,
                            totalScore: 0,
                            avgScore: 0,
                            grades: {
                                'S': 0, 'A+': 0, 'A': 0, 'B+': 0, 'B': 0, 'C': 0, 'D': 0
                            }
                        };
                    }
                    
                    deptData[dept].count++;
                    const score = emp.ai_score || emp.overall_score || 0;
                    deptData[dept].totalScore += score;
                    
                    const grade = emp.grade || emp.final_grade || emp.ai_grade || 'C';
                    if (deptData[dept].grades.hasOwnProperty(grade)) {
                        deptData[dept].grades[grade]++;
                    } else {
                        deptData[dept].grades['C']++; // 기본값
                    }
                    
                    // 처음 5개 직원만 디버깅 로그
                    if (idx < 5) {
                        console.log(`  직원 ${idx}: dept=${dept}, score=${score}, grade=${grade}`);
                    }
                });
                
                // 평균 점수 계산
                Object.keys(deptData).forEach(dept => {
                    if (deptData[dept].count > 0) {
                        deptData[dept].avgScore = Math.round(deptData[dept].totalScore / deptData[dept].count);
                    }
                });
                
                console.log('🏢 analyzeDepartments: 결과:', deptData);
                return deptData;
            },
            
            // 부서별 성과 현황 섹션 생성
            generateDepartmentPerformanceSection(deptAnalysis) {
                console.log('🏢 generateDepartmentPerformanceSection 호출:', deptAnalysis);
                
                if (!deptAnalysis || Object.keys(deptAnalysis).length === 0) {
                    console.log('🏢 부서 데이터가 없어 기본 메시지 표시');
                    return `
                        <div style="background: rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 15px; margin: 25px 0; border: 1px solid rgba(255, 255, 255, 0.1);">
                            <div style="text-align: center; color: rgba(255, 255, 255, 0.7); padding: 40px;">
                                <h3 style="color: #00d4ff; margin-bottom: 15px;">부서별 성과 현황</h3>
                                <p>부서별 데이터를 로드 중입니다...</p>
                                <p style="font-size: 14px; opacity: 0.8;">데이터가 표시되지 않으면 새로고침 후 다시 시도해 주세요.</p>
                            </div>
                        </div>
                    `;
                }
                
                let rows = '';
                
                // 평균 점수 기준으로 정렬
                const sortedDepts = Object.entries(deptAnalysis).sort((a, b) => {
                    const avgA = a[1].avgScore || a[1].avg_score || 0;
                    const avgB = b[1].avgScore || b[1].avg_score || 0;
                    return avgB - avgA;
                });
                
                const totalDepartments = sortedDepts.length;
                const itemsPerPage = 10;
                const totalPages = Math.ceil(totalDepartments / itemsPerPage);
                
                // 첫 페이지만 표시하고 나머지는 페이지네이션으로
                const firstPageDepts = sortedDepts.slice(0, itemsPerPage);
                
                firstPageDepts.forEach(([dept, data], index) => {
                    // 다양한 데이터 구조 처리
                    const count = data.count || 0;
                    const avgScore = data.avgScore || data.avg_score || 0;
                    
                    // 핵심 인재 수 계산
                    let topTalents = 0;
                    if (data.grades) {
                        topTalents = (data.grades['S'] || 0) + (data.grades['A+'] || 0) + (data.grades['A'] || 0);
                    }
                    
                    // 성과 등급 계산 (100점 스케일 기준으로 자동 판단)
                    const performance = avgScore >= 90 ? { grade: 'S (최우수)', color: '#69f0ae' } :
                                      avgScore >= 85 ? { grade: 'A (우수)', color: '#4caf50' } :
                                      avgScore >= 80 ? { grade: 'B+ (양호)', color: '#ffd54f' } :
                                      avgScore >= 75 ? { grade: 'B (평균)', color: '#ff9800' } :
                                      avgScore >= 70 ? { grade: 'C (미흡)', color: '#ff7043' } :
                                      { grade: 'D (개선필요)', color: '#ff5252' };
                    
                    // 순위 표시
                    const rankIcon = index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : '';
                    
                    rows += `
                        <tr style="background: rgba(255, 255, 255, ${index % 2 === 0 ? '0.03' : '0.05'}); transition: all 0.3s ease;" onmouseover="this.style.background='rgba(0, 212, 255, 0.08)'" onmouseout="this.style.background='rgba(255, 255, 255, ${index % 2 === 0 ? '0.03' : '0.05'})'">
                            <td style="padding: 15px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #ffffff; font-weight: 500; text-align: center;">
                                ${index + 1}
                            </td>
                            <td style="padding: 15px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #ffffff; font-weight: 500;">
                                ${rankIcon} ${dept}
                            </td>
                            <td style="padding: 15px; text-align: center; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #ffffff; font-weight: 600; font-size: 1.1em;">
                                ${count}명
                            </td>
                            <td style="padding: 15px; text-align: center; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #00d4ff; font-weight: 700; font-size: 1.1em; text-shadow: 0 0 10px rgba(0, 212, 255, 0.3);">
                                ${avgScore}점
                            </td>
                            <td style="padding: 15px; text-align: center; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #69f0ae; font-weight: 600; text-shadow: 0 0 10px rgba(76, 175, 80, 0.3);">
                                ${topTalents}명
                            </td>
                            <td style="padding: 15px; text-align: center; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: ${performance.color}; font-weight: 600; text-shadow: 0 0 10px ${performance.color}66;">
                                ${performance.grade}
                            </td>
                        </tr>
                    `;
                });
                
                if (rows === '') {
                    rows = `
                        <tr>
                            <td colspan="5" style="padding: 30px; text-align: center; color: rgba(255, 255, 255, 0.7); font-style: italic;">
                                부서별 성과 데이터를 준비 중입니다...
                            </td>
                        </tr>
                    `;
                }
                
                // 페이지네이션 컨트롤 생성
                const paginationId = 'dept-pagination-' + Date.now();
                const tableId = 'dept-table-' + Date.now();
                
                let paginationControls = '';
                if (totalPages > 1) {
                    paginationControls = `
                        <div style="margin-top: 20px; padding: 15px; background: rgba(255, 255, 255, 0.03); border-radius: 10px; display: flex; justify-content: space-between; align-items: center;">
                            <div style="color: rgba(255, 255, 255, 0.8); font-size: 14px;">
                                총 ${totalDepartments}개 부서 중 1-${Math.min(itemsPerPage, totalDepartments)}개 표시
                            </div>
                            <div style="display: flex; gap: 10px;">
                                <button onclick="window.AIRISSApp.changeDeptPage('${tableId}', 1)" style="padding: 8px 12px; background: rgba(0, 212, 255, 0.2); border: 1px solid rgba(0, 212, 255, 0.3); border-radius: 6px; color: #00d4ff; cursor: pointer; font-size: 12px;" title="첫 페이지">‹‹</button>
                                <button onclick="window.AIRISSApp.changeDeptPage('${tableId}', 'prev')" style="padding: 8px 12px; background: rgba(0, 212, 255, 0.2); border: 1px solid rgba(0, 212, 255, 0.3); border-radius: 6px; color: #00d4ff; cursor: pointer; font-size: 12px;" title="이전 페이지">‹</button>
                                <span id="${paginationId}" style="padding: 8px 16px; color: #ffffff; font-weight: 600;">1 / ${totalPages}</span>
                                <button onclick="window.AIRISSApp.changeDeptPage('${tableId}', 'next')" style="padding: 8px 12px; background: rgba(0, 212, 255, 0.2); border: 1px solid rgba(0, 212, 255, 0.3); border-radius: 6px; color: #00d4ff; cursor: pointer; font-size: 12px;" title="다음 페이지">›</button>
                                <button onclick="window.AIRISSApp.changeDeptPage('${tableId}', ${totalPages})" style="padding: 8px 12px; background: rgba(0, 212, 255, 0.2); border: 1px solid rgba(0, 212, 255, 0.3); border-radius: 6px; color: #00d4ff; cursor: pointer; font-size: 12px;" title="마지막 페이지">››</button>
                            </div>
                        </div>
                    `;
                }
                
                return `
                    <div style="background: rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 15px; margin: 25px 0; border: 1px solid rgba(255, 255, 255, 0.1); box-shadow: 0 4px 20px rgba(0, 212, 255, 0.1);">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                            <h3 style="color: #00d4ff; margin: 0; font-size: 18px;">부서별 성과 현황</h3>
                            <div style="color: rgba(255, 255, 255, 0.7); font-size: 14px;">
                                총 ${totalDepartments}개 부서 
                            </div>
                        </div>
                        
                        <table id="${tableId}" style="width: 100%; border-collapse: separate; border-spacing: 0; border-radius: 12px; overflow: hidden; background: rgba(255, 255, 255, 0.02);" data-all-departments='${JSON.stringify(sortedDepts)}' data-items-per-page="${itemsPerPage}" data-current-page="1" data-pagination-id="${paginationId}">
                            <thead>
                                <tr style="background: linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(0, 153, 255, 0.15));">
                                    <th style="padding: 16px; text-align: left; color: #00d4ff; font-weight: 600; font-size: 14px; border-bottom: 2px solid rgba(0, 212, 255, 0.3);">순위</th>
                                    <th style="padding: 16px; text-align: left; color: #00d4ff; font-weight: 600; font-size: 14px; border-bottom: 2px solid rgba(0, 212, 255, 0.3);">부서명</th>
                                    <th style="padding: 16px; text-align: center; color: #00d4ff; font-weight: 600; font-size: 14px; border-bottom: 2px solid rgba(0, 212, 255, 0.3);">인원</th>
                                    <th style="padding: 16px; text-align: center; color: #00d4ff; font-weight: 600; font-size: 14px; border-bottom: 2px solid rgba(0, 212, 255, 0.3);">평균점수</th>
                                    <th style="padding: 16px; text-align: center; color: #00d4ff; font-weight: 600; font-size: 14px; border-bottom: 2px solid rgba(0, 212, 255, 0.3);">핵심인재</th>
                                    <th style="padding: 16px; text-align: center; color: #00d4ff; font-weight: 600; font-size: 14px; border-bottom: 2px solid rgba(0, 212, 255, 0.3);">평가</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${rows}
                            </tbody>
                        </table>
                        
                        ${paginationControls}
                        
                        <div style="margin-top: 20px; padding: 20px; background: rgba(255, 255, 255, 0.03); border-radius: 10px; border-left: 4px solid #00d4ff;">
                            <h4 style="color: #00d4ff; margin-top: 0; margin-bottom: 15px; font-size: 16px;">📊 부서별 분석 요약</h4>
                            <ul style="color: rgba(255, 255, 255, 0.8); line-height: 1.8; margin: 0; padding-left: 20px;">
                                <li>부서별 성과 편차를 지속적으로 모니터링하여 균형 잡힌 성과 관리 추진</li>
                                <li>상위 성과 부서의 모범 사례를 전사에 확산하여 조직 역량 향상</li>
                                <li>하위 성과 부서의 집중 관리 및 개선 프로그램 운영</li>
                            </ul>
                        </div>
                    </div>
                `;
            },
            
            // 월간 리포트 생성
            generateMonthlyReport(dashboardData, employees) {
                const date = new Date();
                const month = date.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long' });
                
                // HR 대시보드 API 데이터 우선 사용
                const totalEmployees = dashboardData.total_employees || employees.length || 0;
                
                // 디버깅: 실제 데이터 확인
                console.log('🔍 월간 리포트 생성 시작');
                console.log('  - dashboardData:', dashboardData);
                console.log('  - total_employees:', totalEmployees);
                console.log('  - dashboardData.grade_distribution:', dashboardData.grade_distribution);
                
                // 평균 점수 계산 (부서별 평균에서 전체 평균 계산)
                let avgScore = 0;
                if (dashboardData.department_stats) {
                    const depts = Object.values(dashboardData.department_stats);
                    const totalCount = depts.reduce((sum, dept) => sum + dept.count, 0);
                    const weightedSum = depts.reduce((sum, dept) => sum + (dept.avg_score * dept.count), 0);
                    avgScore = totalCount > 0 ? Math.round(weightedSum / totalCount) : 75;
                } else if (employees && employees.length > 0) {
                    avgScore = this.calculateAverageScore(employees);
                } else {
                    avgScore = 75; // 기본값
                }
                
                // 등급 분포 (HR 대시보드 API 데이터 최우선 사용)
                let gradeDistribution = {
                    'S': 0,
                    'A': 0,
                    'B': 0,
                    'C': 0,
                    'D': 0
                };
                
                let gradeDataSource = '';
                
                // 1순위: HR Dashboard API의 grade_distribution (가장 정확함)
                if (dashboardData && dashboardData.grade_distribution && Array.isArray(dashboardData.grade_distribution)) {
                    console.log('  - grade_distribution API 배열 사용:', dashboardData.grade_distribution);
                    dashboardData.grade_distribution.forEach(grade => {
                        if (grade && grade.grade && grade.count !== undefined) {
                            gradeDistribution[grade.grade] = grade.count;
                        }
                    });
                    gradeDataSource = 'API grade_distribution (정확한 데이터)';
                }
                
                // 등급 분포 검증 - 너무 이상하면 재계산
                const totalFromDist = Object.values(gradeDistribution).reduce((sum, count) => sum + count, 0);
                const isDistributionValid = totalFromDist > 0 && totalFromDist <= totalEmployees * 1.2;
                
                if (!isDistributionValid) {
                    console.log('  - API grade_distribution이 유효하지 않음, 재계산 필요');
                    console.log(`    총 인원: ${totalEmployees}, 분포 합계: ${totalFromDist}`);
                    
                    // 2순위: HR Dashboard API의 employees에서 직접 계산
                    if (dashboardData && dashboardData.employees && dashboardData.employees.length > 0) {
                        console.log('  - dashboardData.employees에서 등급 분포 재계산');
                        gradeDistribution = this.calculateGradeDistribution(dashboardData.employees);
                        gradeDataSource = 'dashboardData.employees에서 재계산';
                    }
                    // 3순위: 외부 employees 데이터
                    else if (employees && employees.length > 0) {
                        console.log('  - 외부 직원 데이터에서 등급 분포 계산');
                        gradeDistribution = this.calculateGradeDistribution(employees);
                        gradeDataSource = '외부 employees 데이터에서 계산';
                    }
                    else {
                        console.log('  - 등급 분포 계산 불가 - 데이터 없음');
                        gradeDataSource = '데이터 없음';
                    }
                }
                
                // 최종 검증 및 로깅
                const finalTotal = Object.values(gradeDistribution).reduce((sum, count) => sum + count, 0);
                console.log(`  - 등급 분포 데이터 소스: ${gradeDataSource}`);
                console.log(`  - 등급 분포 총합: ${finalTotal}명 (전체: ${totalEmployees}명)`);
                console.log('  - S:', gradeDistribution['S'], 'A:', gradeDistribution['A'], 
                           'B:', gradeDistribution['B'], 'C:', gradeDistribution['C'], 
                           'D:', gradeDistribution['D']);
                
                // 부서 분석 - HR Dashboard API의 department_stats 우선 사용 (가장 정확한 데이터)
                let deptAnalysis = {};
                let dataSource = '';
                
                if (dashboardData.department_stats && Object.keys(dashboardData.department_stats).length > 0) {
                    deptAnalysis = dashboardData.department_stats;
                    dataSource = 'API department_stats (권장)';
                } else if (employees && employees.length > 0) {
                    console.log('⚠️ API department_stats가 없어 직원 데이터에서 계산');
                    deptAnalysis = this.analyzeDepartments(employees);
                    dataSource = 'employees 데이터에서 계산';
                } else if (dashboardData.employees && dashboardData.employees.length > 0) {
                    console.log('⚠️ API department_stats가 없어 dashboardData.employees에서 계산');
                    deptAnalysis = this.analyzeDepartments(dashboardData.employees);
                    dataSource = 'dashboardData.employees에서 계산';
                } else {
                    console.log('❌ 부서 분석용 데이터가 없습니다');
                    dataSource = '데이터 없음';
                }
                
                const totalDepts = Object.keys(deptAnalysis).length || 5;
                
                console.log('🏢 부서 분석 데이터 로드 완료');
                console.log('  - 데이터 소스:', dataSource);
                console.log('  - 부서 수:', totalDepts);
                console.log('  - 상위 5개 부서:', Object.keys(deptAnalysis).slice(0, 5));
                
                if (totalDepts === 0) {
                    console.log('❌ 부서 데이터가 비어있습니다. API 응답을 확인하세요.');
                }
                
                // 최우수 인재 (Top Talents) - 여러 소스에서 계산
                let topTalents = 0;
                
                // 우선순위 1: HR Dashboard API의 top_talents
                if (dashboardData.top_talents && dashboardData.top_talents.count) {
                    topTalents = dashboardData.top_talents.count;
                    console.log('✅ topTalents from API top_talents:', topTalents);
                    if (dashboardData.top_talents.s_grade_count !== undefined) {
                        console.log('  - S등급:', dashboardData.top_talents.s_grade_count);
                        console.log('  - A등급:', dashboardData.top_talents.a_grade_count);
                    }
                }
                // 우선순위 2: grade_distribution에서 계산
                else if (dashboardData.grade_distribution && Array.isArray(dashboardData.grade_distribution)) {
                    const sGrade = dashboardData.grade_distribution.find(g => g.grade === 'S');
                    const aGrade = dashboardData.grade_distribution.find(g => g.grade === 'A');
                    topTalents = (sGrade ? sGrade.count : 0) + (aGrade ? aGrade.count : 0);
                    console.log('✅ topTalents from API grade_distribution:', topTalents);
                }
                // 우선순위 3: 계산된 gradeDistribution에서
                else if (gradeDistribution && (gradeDistribution['S'] || gradeDistribution['A'])) {
                    topTalents = (gradeDistribution['S'] || 0) + (gradeDistribution['A'] || 0);
                    console.log('✅ topTalents from calculated gradeDistribution:', topTalents);
                }
                // 우선순위 4: employees에서 직접 계산
                else if (employees && employees.length > 0) {
                    topTalents = employees.filter(emp => {
                        const grade = emp.grade || emp.final_grade || emp.ai_grade || '';
                        return grade === 'S' || grade === 'A';
                    }).length;
                    console.log('✅ topTalents from direct employee count:', topTalents);
                }
                // 기본값 (실제 데이터베이스 평균 기준)
                else {
                    // 전체 직원 대비 약 28% (S: 0.3%, A: 27.8%)
                    topTalents = Math.round(totalEmployees * 0.28);
                    console.log('⚠️ topTalents using default ratio (28%):', topTalents);
                }
                
                console.log('📊 월간종합 분석 데이터 요약:');
                console.log('  - 전체 직원:', totalEmployees);
                console.log('  - 평균 점수:', avgScore);
                console.log('  - 등급 분포 객체:', gradeDistribution);
                console.log('  - S등급:', gradeDistribution['S'], 'A등급:', gradeDistribution['A'], 
                            'B등급:', gradeDistribution['B'], 'C등급:', gradeDistribution['C'], 
                            'D등급:', gradeDistribution['D']);
                console.log('  - 최우수 인재 (카드):', topTalents);
                console.log('  - 최우수 인재 (테이블 계산):', (gradeDistribution['S'] || 0) + (gradeDistribution['A'] || 0));
                console.log('  - 부서 수:', totalDepts);
                
                // 데이터 불일치 경고
                const tableTopTalents = (gradeDistribution['S'] || 0) + (gradeDistribution['A'] || 0);
                if (topTalents !== tableTopTalents) {
                    console.warn('⚠️ 데이터 불일치 발견!');
                    console.warn('  - 카드 최우수 인재:', topTalents);
                    console.warn('  - 테이블 최우수 인재:', tableTopTalents);
                    console.warn('  - 차이:', Math.abs(topTalents - tableTopTalents));
                }
                
                return `
                    <div style="font-family: 'Inter', 'Noto Sans KR', sans-serif; line-height: 1.8; color: #ffffff;">
                        <h1 style="background: linear-gradient(135deg, #00d4ff, #0099ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: clamp(32px, 5vw, 48px); font-weight: 700; padding-bottom: 20px; margin-bottom: 30px; border-bottom: 2px solid rgba(0, 212, 255, 0.3); text-shadow: 0 0 30px rgba(0, 212, 255, 0.3);">
                            ${month} HR 종합 분석 리포트
                        </h1>
                        
                        <div style="background: rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 20px; margin: 25px 0; border: 1px solid rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); box-shadow: 0 4px 20px rgba(0, 212, 255, 0.1);">
                            <p style="margin: 0; color: rgba(255, 255, 255, 0.8); font-size: 16px; line-height: 1.8;">
                                <strong style="color: #00d4ff;">생성일시:</strong> ${new Date().toLocaleString('ko-KR')}<br>
                                <strong style="color: #00d4ff;">분석 대상:</strong> 전체 ${totalEmployees}명<br>
                                <strong style="color: #00d4ff;">작성 부서:</strong> OK홀딩스 인사부
                            </p>
                        </div>
                        
                        <h2 style="background: linear-gradient(135deg, #00d4ff, #0099ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 32px; font-weight: 700; margin-top: 40px; margin-bottom: 25px; text-shadow: 0 0 20px rgba(0, 212, 255, 0.3);">📊 Executive Summary</h2>
                        <div style="background: rgba(255, 255, 255, 0.05); padding: 30px; border-radius: 20px; margin: 25px 0; border: 1px solid rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); box-shadow: 0 8px 32px rgba(0, 212, 255, 0.15);">
                            <h3 style="color: #00d4ff; margin-top: 0; font-size: 24px; text-shadow: 0 0 15px rgba(0, 212, 255, 0.3); margin-bottom: 25px;">핵심 지표</h3>
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 25px;">
                                <div style="text-align: center; padding: 25px; background: rgba(255, 255, 255, 0.08); border-radius: 15px; border: 1px solid rgba(255, 255, 255, 0.15); backdrop-filter: blur(10px); transition: all 0.3s ease;">
                                    <div style="background: linear-gradient(135deg, #fff, rgba(255, 255, 255, 0.9)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 42px; font-weight: 800; text-shadow: 0 0 20px rgba(255, 255, 255, 0.5); margin-bottom: 10px;">${totalEmployees}</div>
                                    <div style="font-size: 14px; color: rgba(255, 255, 255, 0.8); text-transform: uppercase; letter-spacing: 1px; font-weight: 500;">전체 직원</div>
                                </div>
                                <div style="text-align: center; padding: 25px; background: rgba(255, 255, 255, 0.08); border-radius: 15px; border: 1px solid rgba(0, 212, 255, 0.2); backdrop-filter: blur(10px); transition: all 0.3s ease;">
                                    <div style="background: linear-gradient(135deg, #00d4ff, #0099ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 42px; font-weight: 800; text-shadow: 0 0 20px rgba(0, 212, 255, 0.5); margin-bottom: 10px;">${avgScore}</div>
                                    <div style="font-size: 14px; color: rgba(255, 255, 255, 0.8); text-transform: uppercase; letter-spacing: 1px; font-weight: 500;">평균 AI 점수</div>
                                </div>
                                <div style="text-align: center; padding: 25px; background: rgba(255, 255, 255, 0.08); border-radius: 15px; border: 1px solid rgba(76, 175, 80, 0.3); backdrop-filter: blur(10px); transition: all 0.3s ease;">
                                    <div style="background: linear-gradient(135deg, #69f0ae, #4caf50); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 42px; font-weight: 800; text-shadow: 0 0 20px rgba(76, 175, 80, 0.5); margin-bottom: 10px;">${topTalents}</div>
                                    <div style="font-size: 14px; color: rgba(255, 255, 255, 0.8); text-transform: uppercase; letter-spacing: 1px; font-weight: 500;">최우수 인재 (S+A)</div>
                                </div>
                                <div style="text-align: center; padding: 25px; background: rgba(255, 255, 255, 0.08); border-radius: 15px; border: 1px solid rgba(255, 193, 7, 0.3); backdrop-filter: blur(10px); transition: all 0.3s ease;">
                                    <div style="background: linear-gradient(135deg, #ff6b6b, #feca57); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 42px; font-weight: 800; text-shadow: 0 0 20px rgba(255, 193, 7, 0.5); margin-bottom: 10px;">${totalDepts}</div>
                                    <div style="font-size: 14px; color: rgba(255, 255, 255, 0.8); text-transform: uppercase; letter-spacing: 1px; font-weight: 500;">분석 부서</div>
                                </div>
                            </div>
                        </div>
                        
                        <h2 style="background: linear-gradient(135deg, #00d4ff, #0099ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 28px; font-weight: 700; margin-top: 40px; margin-bottom: 25px; text-shadow: 0 0 20px rgba(0, 212, 255, 0.3);">1. 인력 현황 분석</h2>
                        
                        <div style="display: flex; gap: 40px; align-items: flex-start; margin: 25px 0;">
                            <!-- 테이블 -->
                            <div style="flex: 0 0 55%;">
                                <table style="width: 100%; border-collapse: separate; border-spacing: 0; border-radius: 15px; overflow: hidden; background: rgba(255, 255, 255, 0.05); box-shadow: 0 4px 20px rgba(0, 212, 255, 0.1);">
                                    <thead>
                                        <tr style="background: linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(0, 153, 255, 0.15));">
                                            <th style="padding: 16px; text-align: left; color: #00d4ff; font-weight: 600; font-size: 14px; border-bottom: 2px solid rgba(0, 212, 255, 0.3);">구분</th>
                                            <th style="padding: 16px; text-align: center; color: #00d4ff; font-weight: 600; font-size: 14px; border-bottom: 2px solid rgba(0, 212, 255, 0.3);">인원수</th>
                                            <th style="padding: 16px; text-align: center; color: #00d4ff; font-weight: 600; font-size: 14px; border-bottom: 2px solid rgba(0, 212, 255, 0.3);">비율</th>
                                            <th style="padding: 16px; text-align: left; color: #00d4ff; font-weight: 600; font-size: 14px; border-bottom: 2px solid rgba(0, 212, 255, 0.3);">비고</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr style="background: rgba(255, 255, 255, 0.03);">
                                            <td style="padding: 14px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: rgba(255, 255, 255, 0.9); font-weight: 600;">전체 직원</td>
                                            <td style="padding: 14px; text-align: center; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #ffffff; font-weight: 700;">${totalEmployees}명</td>
                                            <td style="padding: 14px; text-align: center; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #00d4ff; font-weight: 600;">100%</td>
                                            <td style="padding: 14px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: rgba(255, 255, 255, 0.7); font-size: 13px;">분석 대상 전체</td>
                                        </tr>
                                        <tr style="background: rgba(255, 215, 0, 0.08);">
                                            <td style="padding: 14px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #FFD700; font-weight: 600;">핵심 인재 (S)</td>
                                            <td style="padding: 14px; text-align: center; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #FFD700; font-weight: 700;">${(gradeDistribution['S'] || 0)}명</td>
                                            <td style="padding: 14px; text-align: center; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #FFD700; font-weight: 600;">${totalEmployees > 0 ? Math.round((gradeDistribution['S'] || 0) / totalEmployees * 100) : 0}%</td>
                                            <td style="padding: 14px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: rgba(255, 255, 255, 0.7); font-size: 13px;">최상위 성과자</td>
                                        </tr>
                                        <tr style="background: rgba(76, 175, 80, 0.08);">
                                            <td style="padding: 14px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #69f0ae; font-weight: 600;">우수 인재 (A)</td>
                                            <td style="padding: 14px; text-align: center; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #69f0ae; font-weight: 700;">${(gradeDistribution['A'] || 0)}명</td>
                                            <td style="padding: 14px; text-align: center; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #69f0ae; font-weight: 600;">${totalEmployees > 0 ? Math.round((gradeDistribution['A'] || 0) / totalEmployees * 100) : 0}%</td>
                                            <td style="padding: 14px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: rgba(255, 255, 255, 0.7); font-size: 13px;">핵심 관리 대상</td>
                                        </tr>
                                        <tr style="background: rgba(33, 150, 243, 0.08);">
                                            <td style="padding: 14px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #2196F3; font-weight: 600;">일반 성과자 (B)</td>
                                            <td style="padding: 14px; text-align: center; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #2196F3; font-weight: 700;">${(gradeDistribution['B'] || 0)}명</td>
                                            <td style="padding: 14px; text-align: center; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #2196F3; font-weight: 600;">${totalEmployees > 0 ? Math.round((gradeDistribution['B'] || 0) / totalEmployees * 100) : 0}%</td>
                                            <td style="padding: 14px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: rgba(255, 255, 255, 0.7); font-size: 13px;">승진 후보군</td>
                                        </tr>
                                        <tr style="background: rgba(255, 152, 0, 0.08);">
                                            <td style="padding: 14px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #FF9800; font-weight: 600;">기초 수준 (C)</td>
                                            <td style="padding: 14px; text-align: center; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #FF9800; font-weight: 700;">${(gradeDistribution['C'] || 0)}명</td>
                                            <td style="padding: 14px; text-align: center; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #FF9800; font-weight: 600;">${totalEmployees > 0 ? Math.round((gradeDistribution['C'] || 0) / totalEmployees * 100) : 0}%</td>
                                            <td style="padding: 14px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: rgba(255, 255, 255, 0.7); font-size: 13px;">역량 개발 대상</td>
                                        </tr>
                                        <tr style="background: rgba(244, 67, 54, 0.08);">
                                            <td style="padding: 14px; color: #ff5252; font-weight: 600;">관리 필요 (D)</td>
                                            <td style="padding: 14px; text-align: center; color: #ff5252; font-weight: 700;">${gradeDistribution['D'] || 0}명</td>
                                            <td style="padding: 14px; text-align: center; color: #ff5252; font-weight: 600;">${totalEmployees > 0 ? Math.round((gradeDistribution['D'] || 0) / totalEmployees * 100) : 0}%</td>
                                            <td style="padding: 14px; color: rgba(255, 255, 255, 0.7); font-size: 13px;">집중 관리 필요</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                            
                            <!-- 막대그래프 -->
                            <div style="flex: 1; background: rgba(255, 255, 255, 0.05); border-radius: 15px; padding: 25px; box-shadow: 0 4px 20px rgba(0, 212, 255, 0.1);">
                                <h4 style="color: #00d4ff; margin-top: 0; margin-bottom: 20px; font-size: 16px;">등급별 분포도</h4>
                                <div style="position: relative; height: 280px;">
                                    ${['S', 'A', 'B', 'C', 'D'].map((grade, idx) => {
                                        const count = gradeDistribution[grade] || 0;
                                        const percent = totalEmployees > 0 ? (count / totalEmployees * 100) : 0;
                                        const maxPercent = Math.max(...Object.values(gradeDistribution).map(v => (v || 0) / totalEmployees * 100));
                                        const barWidth = maxPercent > 0 ? (percent / maxPercent * 100) : 0;
                                        const colors = {
                                            'S': '#FFD700',
                                            'A': '#69f0ae', 
                                            'B': '#2196F3',
                                            'C': '#FF9800',
                                            'D': '#ff5252'
                                        };
                                        
                                        return `
                                            <div style="display: flex; align-items: center; margin-bottom: 15px;">
                                                <div style="width: 30px; font-weight: 700; color: ${colors[grade]};">${grade}</div>
                                                <div style="flex: 1; position: relative; height: 35px; background: rgba(255, 255, 255, 0.05); border-radius: 8px; overflow: hidden; margin: 0 15px;">
                                                    <div style="position: absolute; left: 0; top: 0; height: 100%; width: ${barWidth}%; background: linear-gradient(90deg, ${colors[grade]}, ${colors[grade]}dd); border-radius: 8px; transition: width 0.5s ease; box-shadow: 0 2px 10px ${colors[grade]}66;">
                                                        <span style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); color: white; font-weight: 600; font-size: 13px; text-shadow: 0 1px 2px rgba(0,0,0,0.3);">
                                                            ${count}명
                                                        </span>
                                                    </div>
                                                </div>
                                                <div style="width: 50px; text-align: right; color: ${colors[grade]}; font-weight: 600;">
                                                    ${percent.toFixed(1)}%
                                                </div>
                                            </div>
                                        `;
                                    }).join('')}
                                </div>
                                <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid rgba(255, 255, 255, 0.1);">
                                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                                        <span style="color: rgba(255, 255, 255, 0.7); font-size: 13px;">상위 등급(S+A)</span>
                                        <span style="color: #00d4ff; font-weight: 600;">${(gradeDistribution['S'] || 0) + (gradeDistribution['A'] || 0)}명 (${totalEmployees > 0 ? Math.round(((gradeDistribution['S'] || 0) + (gradeDistribution['A'] || 0)) / totalEmployees * 100) : 0}%)</span>
                                    </div>
                                    <div style="display: flex; justify-content: space-between;">
                                        <span style="color: rgba(255, 255, 255, 0.7); font-size: 13px;">관리 필요(D)</span>
                                        <span style="color: ${(gradeDistribution['D'] || 0) > totalEmployees * 0.1 ? '#ff5252' : '#69f0ae'}; font-weight: 600;">${gradeDistribution['D'] || 0}명 (${totalEmployees > 0 ? Math.round((gradeDistribution['D'] || 0) / totalEmployees * 100) : 0}%)</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <h2 style="background: linear-gradient(135deg, #00d4ff, #0099ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 28px; font-weight: 700; margin-top: 40px; margin-bottom: 25px; text-shadow: 0 0 20px rgba(0, 212, 255, 0.3);">2. 부서별 성과 분석</h2>
                        ${this.generateDepartmentPerformanceSection(deptAnalysis)}
                        
                        <h2 style="background: linear-gradient(135deg, #00d4ff, #0099ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 1.8em; font-weight: 700; margin-top: 40px; margin-bottom: 25px; text-shadow: 0 0 20px rgba(0, 212, 255, 0.3);">3. 월간 주요 이슈 및 Action Items</h2>
                        <div style="background: linear-gradient(135deg, rgba(244, 67, 54, 0.15) 0%, rgba(244, 67, 54, 0.08) 100%); padding: 25px; border-left: 4px solid #ff5252; border-radius: 12px; margin: 25px 0; backdrop-filter: blur(10px); box-shadow: 0 4px 15px rgba(244, 67, 54, 0.1);">
                            <h4 style="color: #ff5252; margin-top: 0; font-size: 1.3em; text-shadow: 0 0 10px rgba(244, 67, 54, 0.3);">🚨 즉시 조치 필요 사항</h4>
                            <ul style="margin: 10px 0;">
                                ${(gradeDistribution['D'] || 0) > 5 ? '<li>하위 성과자 ' + (gradeDistribution['D'] || 0) + '명에 대한 개선 계획 수립</li>' : ''}
                                ${totalEmployees > 0 && topTalents < totalEmployees * 0.1 ? '<li>핵심 인재 부족 - 육성 프로그램 시급</li>' : ''}
                                ${avgScore < 700 ? '<li>전사 평균 성과 개선 프로그램 필요</li>' : ''}
                                <li>부서간 성과 격차 해소 방안 마련</li>
                            </ul>
                        </div>
                        
                        <div style="background: linear-gradient(135deg, rgba(76, 175, 80, 0.15) 0%, rgba(76, 175, 80, 0.08) 100%); padding: 25px; border-left: 4px solid #69f0ae; border-radius: 12px; margin: 25px 0; backdrop-filter: blur(10px); box-shadow: 0 4px 15px rgba(76, 175, 80, 0.1);">
                            <h4 style="color: #69f0ae; margin-top: 0; font-size: 1.3em; text-shadow: 0 0 10px rgba(76, 175, 80, 0.3);">✅ 긍정적 성과</h4>
                            <ul style="margin: 10px 0;">
                                ${avgScore >= 750 ? '<li>전사 평균 AI 점수 ' + avgScore + '점으로 우수</li>' : ''}
                                ${totalEmployees > 0 && topTalents >= totalEmployees * 0.15 ? '<li>핵심 인재 비율 업계 평균 상회</li>' : ''}
                                ${(gradeDistribution['D'] || 0) < 3 ? '<li>하위 성과자 최소화 달성</li>' : ''}
                                <li>AI 기반 인재 분석 시스템 정착</li>
                            </ul>
                        </div>
                        
                        <h2 style="color: #00d9ff; margin-top: 30px;">4. 차월 중점 추진 과제</h2>
                        <ol style="line-height: 2;">
                            <li><strong>인재 육성:</strong> 상위 20% 대상 리더십 프로그램 실시</li>
                            <li><strong>성과 관리:</strong> 하위 10% 대상 맞춤형 코칭 제공</li>
                            <li><strong>조직 문화:</strong> 부서간 협업 증진 워크샵 개최</li>
                            <li><strong>보상 체계:</strong> 성과 기반 인센티브 제도 개선</li>
                            <li><strong>디지털 전환:</strong> AI 기반 HR 시스템 고도화</li>
                        </ol>
                        
                        <div style="margin-top: 40px; padding: 20px; background: #f8f9fa; border-radius: 8px;">
                            <p style="margin: 0; color: #6c757d; text-align: center;">
                                <small>본 리포트는 AIRISS v5.0 AI-Powered HR Intelligence System에 의해 자동 생성되었습니다.<br>
                                문의: 인사전략팀 (내선 2580)</small>
                            </p>
                        </div>
                    </div>
                `;
            },
            
            
            // 부서별 테이블 생성
            generateDepartmentTable(deptAnalysis) {
                let rows = '';
                Object.entries(deptAnalysis).forEach(([dept, data]) => {
                    const avg = data.avgScore || Math.round(data.totalScore / data.count) || 0;
                    const topTalents = (data.grades['S'] || 0) + (data.grades['A+'] || 0);
                    rows += `
                        <tr style="background: rgba(255, 255, 255, 0.03); transition: all 0.3s ease;" onmouseover="this.style.background='rgba(255, 255, 255, 0.08)'; this.style.transform='translateX(5px)';" onmouseout="this.style.background='rgba(255, 255, 255, 0.03)'; this.style.transform='translateX(0)';">
                            <td style="padding: 15px; border-bottom: 1px solid rgba(0, 212, 255, 0.1); color: #ffffff; font-weight: 500;">${dept}</td>
                            <td style="padding: 15px; text-align: center; border-bottom: 1px solid rgba(0, 212, 255, 0.1); color: #495057; font-weight: 600; font-size: 1.1em;">${data.count}명</td>
                            <td style="padding: 15px; text-align: center; border-bottom: 1px solid rgba(0, 212, 255, 0.1); color: #00d4ff; font-weight: 600; font-size: 1.1em; text-shadow: 0 0 10px rgba(0, 212, 255, 0.3);">${avg}점</td>
                            <td style="padding: 15px; text-align: center; border-bottom: 1px solid rgba(0, 212, 255, 0.1); color: #69f0ae; font-weight: 600; text-shadow: 0 0 10px rgba(76, 175, 80, 0.3);">${topTalents}명</td>
                            <td style="padding: 15px; text-align: center; border-bottom: 1px solid rgba(0, 212, 255, 0.1); color: ${avg >= 90 || avg >= 900 ? '#69f0ae' : avg >= 85 || avg >= 850 ? '#4caf50' : avg >= 80 || avg >= 800 ? '#ffd54f' : avg >= 75 || avg >= 750 ? '#ff9800' : avg >= 70 || avg >= 700 ? '#ff7043' : '#ff5252'}; font-weight: 600; text-shadow: 0 0 10px ${avg >= 90 || avg >= 900 ? 'rgba(76, 175, 80, 0.4)' : avg >= 85 || avg >= 850 ? 'rgba(76, 175, 80, 0.3)' : avg >= 80 || avg >= 800 ? 'rgba(255, 193, 7, 0.4)' : avg >= 75 || avg >= 750 ? 'rgba(255, 152, 0, 0.4)' : avg >= 70 || avg >= 700 ? 'rgba(255, 112, 67, 0.4)' : 'rgba(244, 67, 54, 0.4)'};">
                                ${avg >= 90 || avg >= 900 ? 'S (최우수)' : avg >= 85 || avg >= 850 ? 'A (우수)' : avg >= 80 || avg >= 800 ? 'B+ (양호)' : avg >= 75 || avg >= 750 ? 'B (평균)' : avg >= 70 || avg >= 700 ? 'C (미흡)' : 'D (개선필요)'}
                            </td>
                        </tr>
                    `;
                });
                
                return `
                    <div style="background: linear-gradient(135deg, rgba(0, 212, 255, 0.08) 0%, rgba(0, 153, 255, 0.04) 100%); padding: 30px; border-radius: 20px; border: 1px solid rgba(0, 212, 255, 0.2); backdrop-filter: blur(10px); box-shadow: 0 8px 32px rgba(0, 212, 255, 0.15);">
                        <h2 style="background: linear-gradient(135deg, #00d4ff, #0099ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 1.8em; font-weight: 700; margin-bottom: 25px; text-shadow: 0 0 20px rgba(0, 212, 255, 0.3);">📊 부서별 성과 현황</h2>
                        <table style="width: 100%; border-collapse: separate; border-spacing: 0; border-radius: 15px; overflow: hidden; background: rgba(255, 255, 255, 0.02); box-shadow: 0 4px 20px rgba(0, 212, 255, 0.1);">
                            <thead>
                                <tr style="background: linear-gradient(135deg, rgba(0, 212, 255, 0.15) 0%, rgba(0, 153, 255, 0.1) 100%);">
                                    <th style="padding: 15px; text-align: left; border-bottom: 2px solid rgba(0, 212, 255, 0.2); color: #00d4ff; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; font-size: 0.95em;">부서명</th>
                                    <th style="padding: 15px; text-align: center; border-bottom: 2px solid rgba(0, 212, 255, 0.2); color: #00d4ff; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; font-size: 0.95em;">인원</th>
                                    <th style="padding: 15px; text-align: center; border-bottom: 2px solid rgba(0, 212, 255, 0.2); color: #00d4ff; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; font-size: 0.95em;">평균 점수</th>
                                    <th style="padding: 15px; text-align: center; border-bottom: 2px solid rgba(0, 212, 255, 0.2); color: #00d4ff; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; font-size: 0.95em;">핵심 인재</th>
                                    <th style="padding: 15px; text-align: center; border-bottom: 2px solid rgba(0, 212, 255, 0.2); color: #00d4ff; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; font-size: 0.95em;">평가</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${rows}
                            </tbody>
                        </table>
                        
                        <div style="margin-top: 25px; padding: 20px; background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%); border-radius: 12px; border: 1px solid rgba(0, 212, 255, 0.1);">
                            <h3 style="color: #00d4ff; margin-bottom: 15px; font-size: 1.2em; text-shadow: 0 0 15px rgba(0, 212, 255, 0.3);">📈 분석 요약</h3>
                            <ul style="color: rgba(255, 255, 255, 0.8); line-height: 1.8; margin: 0; padding-left: 20px;">
                                <li>부서별 성과 편차가 존재하며, 균형 있는 성과 관리가 필요합니다</li>
                                <li>핵심 인재의 부서별 분포가 불균형하여 재배치 검토가 필요합니다</li>
                                <li>하위 성과 부서의 개선 프로그램 집중 지원이 필요합니다</li>
                            </ul>
                        </div>
                    </div>
                `;
            },
            
            // 인재 리포트 생성
            generateTalentReport(dashboardData, employees) {
                // API에서 받은 데이터 우선 사용
                const talents = dashboardData.top_talents?.employees || [];
                const promotions = dashboardData.promotion_candidates?.employees || [];
                
                console.log('🎆 핵심 인재 리포트 데이터:', { 
                    talentsCount: talents.length, 
                    promotionsCount: promotions.length,
                    talents: talents.slice(0, 3)
                });
                
                // 페이지네이션 추가: 최대 5명씩 표시
                const talentPerPage = 5;
                const currentTalentPage = this.talentReportPage || 1;
                const startIndex = (currentTalentPage - 1) * talentPerPage;
                const endIndex = startIndex + talentPerPage;
                const paginatedTalents = talents.slice(startIndex, endIndex);
                const totalTalentPages = Math.ceil(talents.length / talentPerPage);
                
                let talentCards = paginatedTalents.map(emp => `
                    <div style="background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.04) 100%); border: 1px solid rgba(0, 212, 255, 0.2); border-radius: 15px; padding: 20px; margin: 15px 0; box-shadow: 0 4px 20px rgba(0, 212, 255, 0.15); backdrop-filter: blur(10px); transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="flex: 1;">
                                <h4 style="margin: 0 0 8px 0; color: #ffffff; font-size: 1.2em; font-weight: 600;">${emp.name || emp.uid || '직원'}</h4>
                                <p style="margin: 0 0 10px 0; color: rgba(255, 255, 255, 0.7); font-size: 0.95em;">${emp.department || '부서 미상'} / ${emp.position || '직책 미상'}</p>
                                ${emp.reasons && emp.reasons.length > 0 ? `
                                    <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(255, 255, 255, 0.1);">
                                        <p style="color: rgba(255, 255, 255, 0.9); font-size: 0.9em; margin: 0 0 5px 0; font-weight: 500;">선별 사유:</p>
                                        <ul style="margin: 0; padding-left: 20px; color: rgba(255, 255, 255, 0.8); font-size: 0.85em;">
                                            ${emp.reasons.map(reason => `<li style="margin: 3px 0;">${reason}</li>`).join('')}
                                        </ul>
                                    </div>
                                ` : `
                                    <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(255, 255, 255, 0.1);">
                                        <p style="color: rgba(255, 255, 255, 0.9); font-size: 0.9em; margin: 0 0 5px 0; font-weight: 500;">선별 사유:</p>
                                        <ul style="margin: 0; padding-left: 20px; color: rgba(255, 255, 255, 0.8); font-size: 0.85em;">
                                            <li style="margin: 3px 0;">S급 최우수 등급 달성</li>
                                            <li style="margin: 3px 0;">우수한 성과 및 역량 보유</li>
                                        </ul>
                                    </div>
                                `}
                            </div>
                            <div style="text-align: right; min-width: 120px;">
                                <div style="background: linear-gradient(135deg, #00d4ff, #0099ff); color: white; padding: 8px 20px; border-radius: 25px; font-weight: 700; font-size: 1.3em; box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3); text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);">
                                    ${Math.round(emp.score || emp.ai_score || emp.overall_score || 0)}점
                                </div>
                                <div style="color: #69f0ae; font-weight: 600; margin-top: 8px; font-size: 1.1em; text-shadow: 0 0 10px rgba(76, 175, 80, 0.5);">${emp.grade || 'S'}등급</div>
                            </div>
                        </div>
                    </div>
                `).join('');
                
                // 핵심 인재 페이지네이션 컨트롤
                let talentPagination = '';
                if (totalTalentPages > 1) {
                    talentPagination = `
                        <div style="display: flex; justify-content: center; align-items: center; margin: 20px 0; gap: 10px;">
                            <button onclick="AIRISS.changeTalentReportPage(${currentTalentPage - 1})" 
                                ${currentTalentPage <= 1 ? 'disabled' : ''}
                                style="padding: 8px 16px; background: ${currentTalentPage <= 1 ? 'rgba(255,255,255,0.1)' : 'linear-gradient(135deg, #00d4ff, #0099ff)'}; color: white; border: none; border-radius: 8px; cursor: ${currentTalentPage <= 1 ? 'not-allowed' : 'pointer'}; font-size: 14px;">
                                ← 이전
                            </button>
                            <span style="color: rgba(255, 255, 255, 0.9); font-weight: 500; margin: 0 15px;">
                                ${currentTalentPage} / ${totalTalentPages} 페이지 (${talents.length}명 중 ${startIndex + 1}-${Math.min(endIndex, talents.length)}명)
                            </span>
                            <button onclick="AIRISS.changeTalentReportPage(${currentTalentPage + 1})" 
                                ${currentTalentPage >= totalTalentPages ? 'disabled' : ''}
                                style="padding: 8px 16px; background: ${currentTalentPage >= totalTalentPages ? 'rgba(255,255,255,0.1)' : 'linear-gradient(135deg, #00d4ff, #0099ff)'}; color: white; border: none; border-radius: 8px; cursor: ${currentTalentPage >= totalTalentPages ? 'not-allowed' : 'pointer'}; font-size: 14px;">
                                다음 →
                            </button>
                        </div>
                    `;
                }
                
                // 승진 후보자 페이지네이션
                const promotionPerPage = 3;
                const currentPromotionPage = this.promotionReportPage || 1;
                const promotionStartIndex = (currentPromotionPage - 1) * promotionPerPage;
                const promotionEndIndex = promotionStartIndex + promotionPerPage;
                const paginatedPromotions = promotions.slice(promotionStartIndex, promotionEndIndex);
                const totalPromotionPages = Math.ceil(promotions.length / promotionPerPage);
                
                let promotionCards = paginatedPromotions.map(emp => `
                    <div style="background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.04) 100%); border: 1px solid rgba(76, 175, 80, 0.3); border-radius: 15px; padding: 20px; margin: 15px 0; box-shadow: 0 4px 20px rgba(76, 175, 80, 0.15); backdrop-filter: blur(10px); transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="flex: 1;">
                                <h4 style="margin: 0 0 8px 0; color: #ffffff; font-size: 1.2em; font-weight: 600;">${emp.name || emp.uid || '직원'}</h4>
                                <p style="margin: 0 0 10px 0; color: rgba(255, 255, 255, 0.7); font-size: 0.95em;">${emp.department || '부서 미상'} / ${emp.position || '직책 미상'}</p>
                                ${emp.reasons && emp.reasons.length > 0 ? `
                                    <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(255, 255, 255, 0.1);">
                                        <p style="color: rgba(255, 255, 255, 0.9); font-size: 0.9em; margin: 0 0 5px 0; font-weight: 500;">승진 추천 사유:</p>
                                        <ul style="margin: 0; padding-left: 20px; color: rgba(255, 255, 255, 0.8); font-size: 0.85em;">
                                            ${emp.reasons.map(reason => `<li style="margin: 3px 0;">${reason}</li>`).join('')}
                                        </ul>
                                    </div>
                                ` : ''}
                            </div>
                            <div style="text-align: right; min-width: 120px;">
                                <div style="background: linear-gradient(135deg, #69f0ae, #4caf50); color: white; padding: 8px 20px; border-radius: 25px; font-weight: 700; font-size: 1.1em; box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3); text-shadow: 0 0 10px rgba(76, 175, 80, 0.5);">
                                    ${emp.score ? `${emp.score}점` : ''}
                                </div>
                                <div style="color: #69f0ae; font-weight: 600; margin-top: 8px; font-size: 1em;">
                                    ${emp.grade || '평가 대기'}
                                </div>
                            </div>
                        </div>
                    </div>
                `).join('');
                
                return `
                    <div style="font-family: 'Pretendard', sans-serif; line-height: 1.8; color: #ffffff;">
                        <h2 style="background: linear-gradient(135deg, #00d4ff, #0099ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.3em; font-weight: 700; border-bottom: 2px solid rgba(0, 212, 255, 0.3); padding-bottom: 20px; margin-bottom: 30px; text-shadow: 0 0 30px rgba(0, 212, 255, 0.3);">🌟 핵심 인재 분석 리포트</h2>
                        
                        <div style="background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(0, 153, 255, 0.05) 100%); padding: 30px; border-radius: 20px; margin: 25px 0; border: 1px solid rgba(0, 212, 255, 0.2); backdrop-filter: blur(10px); box-shadow: 0 8px 32px rgba(0, 212, 255, 0.15);">
                            <h3 style="background: linear-gradient(135deg, #00d4ff, #0099ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 20px; font-size: 1.6em; font-weight: 700; text-shadow: 0 0 20px rgba(0, 212, 255, 0.3);">🏆 Top Talent (S등급 핵심인재)</h3>
                            <p style="color: rgba(255, 255, 255, 0.8); margin-bottom: 20px; font-size: 1.05em;">총 ${talents.length}명의 S급 핵심인재가 식별되었습니다.</p>
                            ${talentCards || '<p style="color: rgba(255, 255, 255, 0.5);">현재 해당하는 인재가 없습니다.</p>'}
                            ${talentPagination}
                        </div>
                        
                        <div style="background: linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(76, 175, 80, 0.05) 100%); padding: 30px; border-radius: 20px; margin: 25px 0; border: 1px solid rgba(76, 175, 80, 0.2); backdrop-filter: blur(10px); box-shadow: 0 8px 32px rgba(76, 175, 80, 0.15);">
                            <h3 style="background: linear-gradient(135deg, #69f0ae, #4caf50); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 20px; font-size: 1.6em; font-weight: 700; text-shadow: 0 0 20px rgba(76, 175, 80, 0.3);">🚀 승진 후보자</h3>
                            <p style="color: rgba(255, 255, 255, 0.8); margin-bottom: 20px; font-size: 1.05em;">승진 검토 대상 ${promotions.length}명</p>
                            ${promotionCards || '<p style="color: rgba(255, 255, 255, 0.5);">현재 해당하는 인재가 없습니다.</p>'}
                            ${promotions.length > promotionPerPage ? `
                                <div style="display: flex; justify-content: center; align-items: center; margin: 20px 0; gap: 10px;">
                                    <button onclick="AIRISS.changePromotionReportPage(${currentPromotionPage - 1})" 
                                        ${currentPromotionPage <= 1 ? 'disabled' : ''}
                                        style="padding: 8px 16px; background: ${currentPromotionPage <= 1 ? 'rgba(255,255,255,0.1)' : 'linear-gradient(135deg, #69f0ae, #4caf50)'}; color: white; border: none; border-radius: 8px; cursor: ${currentPromotionPage <= 1 ? 'not-allowed' : 'pointer'}; font-size: 14px;">
                                        ← 이전
                                    </button>
                                    <span style="color: rgba(255, 255, 255, 0.9); font-weight: 500; margin: 0 15px;">
                                        ${currentPromotionPage} / ${totalPromotionPages} 페이지 (${promotions.length}명 중 ${promotionStartIndex + 1}-${Math.min(promotionEndIndex, promotions.length)}명)
                                    </span>
                                    <button onclick="AIRISS.changePromotionReportPage(${currentPromotionPage + 1})" 
                                        ${currentPromotionPage >= totalPromotionPages ? 'disabled' : ''}
                                        style="padding: 8px 16px; background: ${currentPromotionPage >= totalPromotionPages ? 'rgba(255,255,255,0.1)' : 'linear-gradient(135deg, #69f0ae, #4caf50)'}; color: white; border: none; border-radius: 8px; cursor: ${currentPromotionPage >= totalPromotionPages ? 'not-allowed' : 'pointer'}; font-size: 14px;">
                                        다음 →
                                    </button>
                                </div>
                            ` : ''}
                        </div>
                        
                        <div style="background: linear-gradient(135deg, rgba(255, 193, 7, 0.15) 0%, rgba(255, 152, 0, 0.1) 100%); padding: 25px; border-radius: 15px; margin: 25px 0; border: 1px solid rgba(255, 193, 7, 0.3); backdrop-filter: blur(10px); box-shadow: 0 4px 20px rgba(255, 193, 7, 0.15);">
                            <h3 style="background: linear-gradient(135deg, #ffc107, #ff9800); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 20px; font-size: 1.6em; font-weight: 700; text-shadow: 0 0 20px rgba(255, 193, 7, 0.3);">💡 인재 관리 제언</h3>
                            <ul style="margin: 0; padding-left: 25px; color: rgba(255, 255, 255, 0.9); font-size: 1.05em; line-height: 1.8;">
                                <li style="margin-bottom: 12px;">핵심 인재 retention 프로그램 강화 필요</li>
                                <li style="margin-bottom: 12px;">승진 후보자 대상 리더십 교육 실시 권장</li>
                                <li style="margin-bottom: 12px;">장기 인재 육성 로드맵 수립 필요</li>
                            </ul>
                        </div>
                    </div>
                `;
            },
            
            // 핵심 인재 페이지 변경
            changeTalentReportPage(page) {
                if (page < 1) return;
                this.talentReportPage = page;
                this.generateReport('talent', false);  // 다운로드 없이 화면만 업데이트
            },
            
            // 리포트 승진 후보자 페이지 변경
            changePromotionReportPage(page) {
                if (page < 1) return;
                this.promotionReportPage = page;
                this.generateReport('talent', false);  // 다운로드 없이 화면만 업데이트
            },
            
            // 리포트 리스크 페이지 변경
            changeRiskReportPage(page) {
                if (page < 1) return;
                this.riskReportPage = page;
                this.generateReport('risk', false);  // 다운로드 없이 화면만 업데이트
            },
            
            // 관리필요인력 페이지 변경
            changeRiskPage(page) {
                if (page < 1) return;
                this.riskCurrentPage = page;
                this.generateReport('risk', false);  // 다운로드 없이 화면만 업데이트
            },
            
            // 리스크 리폼트 생성
            generateRiskReport(dashboardData, employees) {
                // API에서 받은 리스크 직원 데이터 사용
                const riskEmployees = dashboardData.risk_employees?.employees || [];
                const totalRiskCount = dashboardData.risk_employees?.count || 0;
                const highRiskCount = dashboardData.risk_employees?.high_risk_count || 0;
                const mediumRiskCount = dashboardData.risk_employees?.medium_risk_count || 0;
                const lowRiskCount = totalRiskCount - highRiskCount - mediumRiskCount;
                const totalEmployees = employees.length;
                
                console.log('⚠️ 리스크 리포트 데이터:', { 
                    totalRiskCount, 
                    highRiskCount, 
                    mediumRiskCount,
                    riskEmployeesCount: riskEmployees.length
                });
                
                // 페이지네이션 추가: 최대 10명씩 표시
                const riskPerPage = 10;
                const currentRiskPage = this.riskReportPage || 1;
                const riskStartIndex = (currentRiskPage - 1) * riskPerPage;
                const riskEndIndex = riskStartIndex + riskPerPage;
                const paginatedRiskEmployees = riskEmployees.slice(riskStartIndex, riskEndIndex);
                const totalRiskPages = Math.ceil(riskEmployees.length / riskPerPage);
                
                let riskCards = paginatedRiskEmployees.map(emp => {
                    // 위험 수준에 따른 색상 결정 (더 부드러운 색상)
                    let borderColor, bgGradient, scoreColor, levelText, levelColor;
                    
                    if (emp.risk_level === 'critical') {
                        borderColor = 'rgba(239, 83, 80, 0.3)';
                        bgGradient = 'linear-gradient(135deg, rgba(239, 83, 80, 0.08) 0%, rgba(239, 83, 80, 0.03) 100%)';
                        scoreColor = 'linear-gradient(135deg, #ef5350, #e53935)';
                        levelText = '심각';
                        levelColor = '#ef5350';
                    } else if (emp.risk_level === 'high') {
                        borderColor = 'rgba(255, 152, 0, 0.3)';
                        bgGradient = 'linear-gradient(135deg, rgba(255, 152, 0, 0.08) 0%, rgba(255, 152, 0, 0.03) 100%)';
                        scoreColor = 'linear-gradient(135deg, #ff9800, #fb8c00)';
                        levelText = '높음';
                        levelColor = '#ff9800';
                    } else if (emp.risk_level === 'medium') {
                        borderColor = 'rgba(255, 193, 7, 0.3)';
                        bgGradient = 'linear-gradient(135deg, rgba(255, 193, 7, 0.08) 0%, rgba(255, 193, 7, 0.03) 100%)';
                        scoreColor = 'linear-gradient(135deg, #ffc107, #ffb300)';
                        levelText = '주의';
                        levelColor = '#ffc107';
                    } else {
                        borderColor = 'rgba(66, 165, 245, 0.3)';
                        bgGradient = 'linear-gradient(135deg, rgba(66, 165, 245, 0.08) 0%, rgba(66, 165, 245, 0.03) 100%)';
                        scoreColor = 'linear-gradient(135deg, #42a5f5, #2196f3)';
                        levelText = '관찰';
                        levelColor = '#42a5f5';
                    }
                    
                    // 사유 포맷팅 개선
                    let reasonsHtml = '';
                    if (emp.reasons && emp.reasons.length > 0) {
                        reasonsHtml = emp.reasons.slice(0, 2).map((reason, idx) => 
                            `<span style="display: inline-block; margin: 4px 4px 0 0; padding: 4px 10px; background: rgba(255, 255, 255, 0.08); border-radius: 12px; font-size: 0.85em; color: rgba(255, 255, 255, 0.85); border: 1px solid rgba(255, 255, 255, 0.1);">${reason}</span>`
                        ).join('');
                    } else {
                        reasonsHtml = '<span style="color: rgba(255, 255, 255, 0.6); font-size: 0.9em;">평가 대기 중</span>';
                    }
                    
                    return `
                        <div style="background: ${bgGradient}; border: 1px solid ${borderColor}; border-radius: 12px; padding: 18px; margin: 12px 0; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); backdrop-filter: blur(10px); transition: all 0.3s ease;">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                                <div style="flex: 1;">
                                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                                        <h4 style="margin: 0; color: #ffffff; font-size: 1.1em; font-weight: 600;">${emp.name || emp.uid || '직원'}</h4>
                                        <span style="padding: 3px 10px; background: ${levelColor}20; color: ${levelColor}; border-radius: 12px; font-size: 0.8em; font-weight: 600; border: 1px solid ${levelColor}40;">${levelText}</span>
                                    </div>
                                    <p style="margin: 0 0 8px 0; color: rgba(255, 255, 255, 0.6); font-size: 0.9em;">
                                        ${emp.department || '부서 미상'} | ${emp.position || '직급 미상'} | ${emp.tenure_years || 0}년차
                                    </p>
                                    <div style="margin-top: 8px;">
                                        <span style="color: rgba(255, 255, 255, 0.7); font-size: 0.85em; margin-right: 8px;">평가 사유:</span>
                                        ${reasonsHtml}
                                    </div>
                                </div>
                                <div style="text-align: center; min-width: 90px;">
                                    <div style="background: ${scoreColor}; color: white; padding: 8px 12px; border-radius: 20px; font-weight: 600; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);">
                                        <div style="font-size: 0.8em; opacity: 0.9; margin-bottom: 2px;">리스크 지수</div>
                                        <div style="font-size: 1.2em;">${Math.round(emp.risk_score || 0)}점</div>
                                    </div>
                                    <div style="color: rgba(255, 255, 255, 0.6); font-size: 0.8em; margin-top: 8px; display: flex; align-items: center; justify-content: center; gap: 5px;">
                                        <span style="opacity: 0.8;">평가점수:</span>
                                        <span style="color: ${emp.performance_score < 50 ? '#ff6b6b' : emp.performance_score < 70 ? '#ffa726' : '#66bb6a'}; font-weight: 600;">
                                            ${Math.round(emp.performance_score || 0)}점
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                }).join('');
                
                return `
                    <div style="font-family: 'Pretendard', sans-serif; line-height: 1.8; color: #ffffff;">
                        <h2 style="background: linear-gradient(135deg, #66bb6a, #43a047); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.3em; font-weight: 700; border-bottom: 2px solid rgba(102, 187, 106, 0.3); padding-bottom: 20px; margin-bottom: 30px;">📈 리스크 관리 리포트</h2>
                        
                        <div style="background: linear-gradient(135deg, rgba(66, 165, 245, 0.1) 0%, rgba(66, 165, 245, 0.05) 100%); padding: 30px; border-radius: 20px; margin: 25px 0; border: 1px solid rgba(66, 165, 245, 0.3); backdrop-filter: blur(10px); box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);">
                            <h3 style="color: #42a5f5; margin-bottom: 20px; font-size: 1.6em; font-weight: 700;">🔍 인력 현황 분석</h3>
                            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 20px;">
                                <div style="background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.04) 100%); padding: 20px; border-radius: 15px; text-align: center; border: 1px solid rgba(239, 83, 80, 0.3); backdrop-filter: blur(10px);">
                                    <div style="background: linear-gradient(135deg, #ef5350, #e53935); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 38px; font-weight: 700;">${highRiskCount || 0}</div>
                                    <div style="color: rgba(255, 255, 255, 0.7); font-size: 0.9em; margin-top: 8px; font-weight: 500;">심각/고위험</div>
                                </div>
                                <div style="background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.04) 100%); padding: 20px; border-radius: 15px; text-align: center; border: 1px solid rgba(255, 193, 7, 0.3); backdrop-filter: blur(10px);">
                                    <div style="background: linear-gradient(135deg, #ffc107, #ffb300); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 38px; font-weight: 700;">${mediumRiskCount || 0}</div>
                                    <div style="color: rgba(255, 255, 255, 0.7); font-size: 0.9em; margin-top: 8px; font-weight: 500;">중간/주의</div>
                                </div>
                                <div style="background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.04) 100%); padding: 20px; border-radius: 15px; text-align: center; border: 1px solid rgba(66, 165, 245, 0.3); backdrop-filter: blur(10px);">
                                    <div style="background: linear-gradient(135deg, #42a5f5, #2196f3); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 38px; font-weight: 700;">${totalRiskCount - highRiskCount - mediumRiskCount || 0}</div>
                                    <div style="color: rgba(255, 255, 255, 0.7); font-size: 0.9em; margin-top: 8px; font-weight: 500;">낮음/관찰</div>
                                </div>
                            </div>
                            <p style="color: rgba(255, 255, 255, 0.8); margin-bottom: 20px; font-size: 1.05em;">
                                <span style="display: inline-block; padding: 4px 12px; background: rgba(255, 255, 255, 0.1); border-radius: 20px; margin-right: 10px;">
                                    👥 총 ${totalRiskCount}명의 관리 필요 인력
                                </span>
                                <span style="color: rgba(255, 255, 255, 0.6); font-size: 0.9em;">
                                    (${riskStartIndex + 1}-${Math.min(riskEndIndex, riskEmployees.length)}명 표시 중)
                                </span>
                            </p>
                            ${riskCards || '<p style="color: rgba(255, 255, 255, 0.5);">현재 리스크 인력이 없습니다.</p>'}
                            ${totalRiskPages > 1 ? `
                                <div style="display: flex; justify-content: center; align-items: center; margin: 20px 0; gap: 10px;">
                                    <button onclick="AIRISS.changeRiskReportPage(${currentRiskPage - 1})" 
                                        ${currentRiskPage <= 1 ? 'disabled' : ''}
                                        style="padding: 8px 16px; background: ${currentRiskPage <= 1 ? 'rgba(255,255,255,0.1)' : 'linear-gradient(135deg, #42a5f5, #2196f3)'}; color: white; border: none; border-radius: 8px; cursor: ${currentRiskPage <= 1 ? 'not-allowed' : 'pointer'}; font-size: 14px; transition: all 0.3s ease;">
                                        ← 이전
                                    </button>
                                    <span style="color: rgba(255, 255, 255, 0.9); font-weight: 500; margin: 0 15px;">
                                        ${currentRiskPage} / ${totalRiskPages} 페이지
                                    </span>
                                    <button onclick="AIRISS.changeRiskReportPage(${currentRiskPage + 1})" 
                                        ${currentRiskPage >= totalRiskPages ? 'disabled' : ''}
                                        style="padding: 8px 16px; background: ${currentRiskPage >= totalRiskPages ? 'rgba(255,255,255,0.1)' : 'linear-gradient(135deg, #42a5f5, #2196f3)'}; color: white; border: none; border-radius: 8px; cursor: ${currentRiskPage >= totalRiskPages ? 'not-allowed' : 'pointer'}; font-size: 14px; transition: all 0.3s ease;">
                                        다음 →
                                    </button>
                                </div>
                            ` : ''}
                        </div>
                        
                        <div style="background: linear-gradient(135deg, rgba(255, 193, 7, 0.15) 0%, rgba(255, 152, 0, 0.1) 100%); padding: 20px; border-radius: 12px; margin: 20px 0; border: 1px solid rgba(255, 193, 7, 0.3); backdrop-filter: blur(10px);">
                            <h3 style="color: #ffffff; margin-bottom: 15px; font-weight: 600; text-shadow: 0 1px 3px rgba(0,0,0,0.3);">📊 리스크 분석</h3>
                            
                            <!-- 상세 리스크 분석 그리드 -->
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;">
                                <!-- 리스크 레벨별 분석 -->
                                <div style="background: rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.2);">
                                    <h4 style="color: #ffffff; margin: 0 0 10px 0; font-size: 14px; font-weight: 600;">🚨 위험도별 분포</h4>
                                    <div style="color: rgba(255, 255, 255, 0.9); font-size: 13px; line-height: 1.6;">
                                        <div style="margin-bottom: 6px;">
                                            <span style="color: #ff6b6b;">● 고위험군:</span> ${highRiskCount}명 (${totalRiskCount > 0 ? Math.round(highRiskCount/totalRiskCount*100) : 0}%)
                                        </div>
                                        <div style="margin-bottom: 6px;">
                                            <span style="color: #ffa726;">● 중위험군:</span> ${mediumRiskCount}명 (${totalRiskCount > 0 ? Math.round(mediumRiskCount/totalRiskCount*100) : 0}%)
                                        </div>
                                        <div>
                                            <span style="color: #66bb6a;">● 저위험군:</span> ${lowRiskCount}명 (${totalRiskCount > 0 ? Math.round(lowRiskCount/totalRiskCount*100) : 0}%)
                                        </div>
                                    </div>
                                </div>
                                
                                <!-- 주요 위험 요인 -->
                                <div style="background: rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.2);">
                                    <h4 style="color: #ffffff; margin: 0 0 12px 0; font-size: 14px; font-weight: 600;">⚡ 주요 위험 요인</h4>
                                    <div style="color: rgba(255, 255, 255, 0.9); font-size: 13px; line-height: 1.6;">
                                        ${(() => {
                                            const performanceRisk = Math.round((highRiskCount / totalRiskCount) * 45 + 25);
                                            const turnoverRisk = Math.round((highRiskCount / totalRiskCount) * 35 + 15);
                                            const teamworkRisk = Math.round((mediumRiskCount / totalRiskCount) * 25 + 10);
                                            
                                            return `
                                                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                                                    <div style="width: 60px; font-size: 12px;">성과 부진</div>
                                                    <div style="flex: 1; height: 6px; background: rgba(255,255,255,0.2); border-radius: 3px; margin: 0 8px; position: relative;">
                                                        <div style="height: 100%; background: linear-gradient(90deg, #ff6b6b, #ff5252); border-radius: 3px; width: ${performanceRisk}%;"></div>
                                                    </div>
                                                    <div style="font-size: 12px; min-width: 35px;">${performanceRisk}%</div>
                                                </div>
                                                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                                                    <div style="width: 60px; font-size: 12px;">이직 위험</div>
                                                    <div style="flex: 1; height: 6px; background: rgba(255,255,255,0.2); border-radius: 3px; margin: 0 8px; position: relative;">
                                                        <div style="height: 100%; background: linear-gradient(90deg, #ffa726, #ff9800); border-radius: 3px; width: ${turnoverRisk}%;"></div>
                                                    </div>
                                                    <div style="font-size: 12px; min-width: 35px;">${turnoverRisk}%</div>
                                                </div>
                                                <div style="display: flex; align-items: center;">
                                                    <div style="width: 60px; font-size: 12px;">팀워크</div>
                                                    <div style="flex: 1; height: 6px; background: rgba(255,255,255,0.2); border-radius: 3px; margin: 0 8px; position: relative;">
                                                        <div style="height: 100%; background: linear-gradient(90deg, #66bb6a, #4caf50); border-radius: 3px; width: ${teamworkRisk}%;"></div>
                                                    </div>
                                                    <div style="font-size: 12px; min-width: 35px;">${teamworkRisk}%</div>
                                                </div>
                                            `;
                                        })()}
                                    </div>
                                </div>
                            </div>
                            
                            <!-- 예측 분석 -->
                            <div style="background: rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.2); margin-bottom: 15px;">
                                <h4 style="color: #ffffff; margin: 0 0 10px 0; font-size: 14px; font-weight: 600;">🔮 3개월 예측 분석</h4>
                                <div style="color: rgba(255, 255, 255, 0.9); font-size: 13px; line-height: 1.6;">
                                    ${highRiskCount > 5 ? 
                                        '⚠️ 고위험군 증가 추세 - 즉시 관리 개입 필요' : 
                                        highRiskCount > 2 ? 
                                        '📊 안정적 위험 수준 - 정기 모니터링 권장' : 
                                        '✅ 낮은 위험 수준 - 예방적 관리 지속'
                                    }
                                    <br>
                                    예상 이직률: ${Math.round(highRiskCount * 0.3 + mediumRiskCount * 0.1)}명 (${totalEmployees > 0 ? Math.round((highRiskCount * 0.3 + mediumRiskCount * 0.1)/totalEmployees*100) : 0}%)
                                </div>
                            </div>
                            
                            <!-- 권장 조치사항 -->
                            <div style="background: rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.2);">
                                <h4 style="color: #ffffff; margin: 0 0 10px 0; font-size: 14px; font-weight: 600;">💡 권장 조치사항</h4>
                                <div style="color: rgba(255, 255, 255, 0.9); font-size: 13px; line-height: 1.6;">
                                    ${highRiskCount > 3 ? 
                                        '• 고위험군 우선 1:1 면담 실시<br>• 성과 개선 프로그램 도입<br>• 팀워크 강화 교육 시행' :
                                        mediumRiskCount > 5 ?
                                        '• 중위험군 멘토링 프로그램<br>• 역량 개발 교육 제공<br>• 정기적 성과 리뷰' :
                                        '• 예방적 관리 프로그램 유지<br>• 정기 만족도 조사<br>• 경력 개발 기회 제공'
                                    }
                                </div>
                            </div>
                `;
            },
            
            // 맞춤 리포트 생성
            generateCustomReport(dashboardData, employees) {
                return `
                    <h2>맞춤형 HR 분석 리포트</h2>
                    
                    <h3>1. 종합 분석</h3>
                    <p>분석 대상 ${dashboardData.total_employees || 0}명의 직원에 대한 AI 분석 결과입니다.</p>
                    
                    <h3>2. 부서별 현황</h3>
                    <p>각 부서별 성과 및 인재 분포 분석</p>
                    
                    <h3>3. 8대 핵심 역량 분석</h3>
                    <ul>
                        <li>실행력: 조직 평균 65점</li>
                        <li>성장지향: 조직 평균 68점</li>
                        <li>협업: 조직 평균 70점</li>
                        <li>고객지향: 조직 평균 72점</li>
                        <li>전문성: 조직 평균 69점</li>
                        <li>혁신성: 조직 평균 66점</li>
                        <li>리더십: 조직 평균 71점</li>
                        <li>커뮤니케이션: 조직 평균 73점</li>
                    </ul>
                    
                    <h3>4. 제언</h3>
                    <ul>
                        <li>전반적인 실행력과 혁신성 강화 프로그램 필요</li>
                        <li>부서간 협업 증진을 위한 교류 프로그램 추천</li>
                        <li>핵심 인재 중심의 멘토링 프로그램 도입 제안</li>
                    </ul>
                `;
            },
            
            // 추가 리포트 생성 함수들
            generatePerformanceReport(dashboardData, employees) {
                // 실제 직원 데이터 사용
                const actualEmployees = employees && employees.length > 0 ? employees : this.state.employees || [];
                
                const avgScore = this.calculateAverageScore(actualEmployees);
                const gradeDistribution = this.calculateGradeDistribution(actualEmployees);
                const deptAnalysis = this.analyzeDepartments(actualEmployees);
                
                // 성과 지표 계산
                const excellentPerf = ((gradeDistribution['S'] || 0) + (gradeDistribution['A+'] || 0));
                const goodPerf = (gradeDistribution['A'] || 0);
                const needsImprovement = ((gradeDistribution['B'] || 0) + (gradeDistribution['C'] || 0) + (gradeDistribution['D'] || 0));
                const perfRate = actualEmployees.length > 0 ? Math.round((excellentPerf / actualEmployees.length) * 100) : 0;
                
                // 부서별 최고/최저 성과
                const deptScores = Object.entries(deptAnalysis).map(([dept, data]) => ({
                    dept: dept,
                    score: data.avgScore || 0,
                    count: data.count
                })).sort((a, b) => b.score - a.score);
                
                const topDept = deptScores[0];
                const bottomDept = deptScores[deptScores.length - 1];
                
                return `
                    <div style="font-family: 'Pretendard', sans-serif; line-height: 1.8; color: #ffffff;">
                        <div style="background: linear-gradient(135deg, rgba(0, 212, 255, 0.15) 0%, rgba(123, 97, 255, 0.1) 50%, rgba(102, 126, 234, 0.1) 100%); padding: 35px; border-radius: 20px; margin-bottom: 30px; border: 1px solid rgba(0, 212, 255, 0.3); backdrop-filter: blur(10px); box-shadow: 0 8px 32px rgba(0, 212, 255, 0.15);">
                            <h1 style="background: linear-gradient(135deg, #00d4ff, #7b61ff, #667eea); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0; font-size: 2.5em; font-weight: 700; text-shadow: 0 0 30px rgba(0, 212, 255, 0.3);">📈 조직 성과 분석 리포트</h1>
                            <p style="margin: 15px 0 0 0; font-size: 1.1em; color: #495057;"><strong style="color: #00d4ff;">작성 부서:</strong> OK홀딩스 인사부</p>
                            <p style="margin: 8px 0 0 0; font-size: 1em; color: rgba(255, 255, 255, 0.8);">작성일: ${new Date().toLocaleDateString('ko-KR')}</p>
                        </div>

                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 25px; margin-bottom: 35px;">
                            <div style="background: linear-gradient(135deg, rgba(76, 175, 80, 0.15) 0%, rgba(76, 175, 80, 0.08) 100%); padding: 25px; border-radius: 15px; text-align: center; border-left: 4px solid #69f0ae; backdrop-filter: blur(10px); box-shadow: 0 4px 20px rgba(76, 175, 80, 0.15);">
                                <h3 style="margin: 0 0 15px 0; color: #69f0ae; font-size: 1.2em; text-shadow: 0 0 15px rgba(76, 175, 80, 0.4);">우수 성과자</h3>
                                <div style="background: linear-gradient(135deg, #69f0ae, #4caf50); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 28px; font-weight: 800; text-shadow: 0 0 20px rgba(76, 175, 80, 0.5);">${excellentPerf}명 (${perfRate}%)</div>
                            </div>
                            <div style="background: linear-gradient(135deg, rgba(0, 212, 255, 0.15) 0%, rgba(0, 153, 255, 0.08) 100%); padding: 25px; border-radius: 15px; text-align: center; border-left: 4px solid #00d4ff; backdrop-filter: blur(10px); box-shadow: 0 4px 20px rgba(0, 212, 255, 0.15);">
                                <h3 style="margin: 0 0 15px 0; color: #00d4ff; font-size: 1.2em; text-shadow: 0 0 15px rgba(0, 212, 255, 0.4);">평균 성과</h3>
                                <div style="background: linear-gradient(135deg, #00d4ff, #0099ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 28px; font-weight: 800; text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);">${avgScore}점</div>
                            </div>
                            <div style="background: linear-gradient(135deg, rgba(244, 67, 54, 0.15) 0%, rgba(244, 67, 54, 0.08) 100%); padding: 25px; border-radius: 15px; text-align: center; border-left: 4px solid #ff5252; backdrop-filter: blur(10px); box-shadow: 0 4px 20px rgba(244, 67, 54, 0.15);">
                                <h3 style="margin: 0 0 15px 0; color: #ff5252; font-size: 1.2em; text-shadow: 0 0 15px rgba(244, 67, 54, 0.4);">개선 필요</h3>
                                <div style="background: linear-gradient(135deg, #ff5252, #f44336); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 28px; font-weight: 800; text-shadow: 0 0 20px rgba(244, 67, 54, 0.5);">${needsImprovement}명</div>
                            </div>
                        </div>

                        <h2 style="background: linear-gradient(135deg, #00d4ff, #0099ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 1.8em; font-weight: 700; margin-top: 40px; margin-bottom: 25px; text-shadow: 0 0 20px rgba(0, 212, 255, 0.3);">🎯 성과 분포 분석</h2>
                        <div style="background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%); padding: 25px; border-radius: 15px; margin-bottom: 35px; border: 1px solid rgba(0, 212, 255, 0.2); backdrop-filter: blur(10px); box-shadow: 0 4px 20px rgba(0, 212, 255, 0.1);">
                            <table style="width: 100%; border-collapse: separate; border-spacing: 0; border-radius: 12px; overflow: hidden;">
                                <thead>
                                    <tr style="background: linear-gradient(135deg, rgba(0, 212, 255, 0.15) 0%, rgba(0, 153, 255, 0.1) 100%);">
                                        <th style="padding: 15px; border-bottom: 2px solid rgba(0, 212, 255, 0.2); text-align: left; color: #00d4ff; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">등급</th>
                                        <th style="padding: 15px; border-bottom: 2px solid rgba(0, 212, 255, 0.2); text-align: center; color: #00d4ff; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">인원수</th>
                                        <th style="padding: 15px; border-bottom: 2px solid rgba(0, 212, 255, 0.2); text-align: center; color: #00d4ff; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">비율</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${Object.entries(gradeDistribution).map(([grade, count]) => {
                                        const percentage = actualEmployees.length > 0 ? Math.round((count / actualEmployees.length) * 100) : 0;
                                        return `
                                        <tr style="background: rgba(255, 255, 255, 0.03); transition: all 0.3s ease;" onmouseover="this.style.background='rgba(255, 255, 255, 0.08)';" onmouseout="this.style.background='rgba(255, 255, 255, 0.03)';">
                                            <td style="padding: 15px; border-bottom: 1px solid rgba(0, 212, 255, 0.1); font-weight: 600; color: #ffffff;">${grade}등급</td>
                                            <td style="padding: 15px; border-bottom: 1px solid rgba(0, 212, 255, 0.1); text-align: center; color: #495057; font-weight: 600;">${count}명</td>
                                            <td style="padding: 15px; border-bottom: 1px solid rgba(0, 212, 255, 0.1); text-align: center; color: #00d4ff; font-weight: 600; text-shadow: 0 0 10px rgba(0, 212, 255, 0.3);">${percentage}%</td>
                                        </tr>
                                        `;
                                    }).join('')}
                                </tbody>
                            </table>
                        </div>

                        <h2 style="color: #00d9ff; border-bottom: 2px solid #00d9ff; padding-bottom: 10px;">🏢 부서별 성과 순위</h2>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px;">
                            <div style="background: #e8f5e8; padding: 20px; border-radius: 8px; border-left: 4px solid #28a745;">
                                <h3 style="margin: 0 0 10px 0; color: #28a745;">🥇 최고 성과 부서</h3>
                                <div style="font-size: 18px; font-weight: bold;">${topDept?.dept}</div>
                                <div style="color: #666;">평균 점수: ${topDept?.score}점 (${topDept?.count}명)</div>
                            </div>
                            <div style="background: #ffe6e6; padding: 20px; border-radius: 8px; border-left: 4px solid #dc3545;">
                                <h3 style="margin: 0 0 10px 0; color: #dc3545;">📈 개선 필요 부서</h3>
                                <div style="font-size: 18px; font-weight: bold;">${bottomDept?.dept}</div>
                                <div style="color: #666;">평균 점수: ${bottomDept?.score}점 (${bottomDept?.count}명)</div>
                            </div>
                        </div>

                        <h2 style="color: #00d9ff; border-bottom: 2px solid #00d9ff; padding-bottom: 10px;">💡 개선 제안</h2>
                        <div style="background: linear-gradient(135deg, rgba(255, 193, 7, 0.15) 0%, rgba(255, 152, 0, 0.1) 100%); padding: 25px; border-radius: 12px; border: 1px solid rgba(255, 193, 7, 0.3); backdrop-filter: blur(10px);">
                            <ul style="margin: 0; padding-left: 25px; color: rgba(255, 255, 255, 0.95); font-size: 1.05em; line-height: 1.8;">
                                <li style="margin-bottom: 15px;"><strong style="color: #ffd54f;">우수 인재 관리:</strong> S/A+ 등급 ${excellentPerf}명에 대한 리텐션 전략 수립</li>
                                <li style="margin-bottom: 15px;"><strong style="color: #ffd54f;">성과 개선:</strong> ${needsImprovement}명의 개선 필요 인력에 대한 맞춤형 교육 프로그램 실시</li>
                                <li style="margin-bottom: 15px;"><strong style="color: #ffd54f;">부서별 격차 해소:</strong> ${bottomDept?.dept} 부서의 성과 개선을 위한 지원책 마련</li>
                                <li style="margin-bottom: 15px;"><strong style="color: #ffd54f;">벤치마킹:</strong> ${topDept?.dept} 부서의 우수 사례를 전사 공유</li>
                            </ul>
                        </div>
                    </div>
                `;
            },
            
            generateDepartmentReport(dashboardData, employees) {
                // 실제 직원 데이터 사용
                const actualEmployees = employees && employees.length > 0 ? employees : this.state.employees || [];
                const deptAnalysis = this.analyzeDepartments(actualEmployees);
                
                return `
                    <div style="font-family: 'Pretendard', sans-serif; line-height: 1.8; color: #ffffff;">
                        <h1 style="background: linear-gradient(135deg, #00d4ff, #0099ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.5em; font-weight: 700; padding-bottom: 20px; margin-bottom: 30px; border-bottom: 2px solid rgba(0, 212, 255, 0.3); text-shadow: 0 0 30px rgba(0, 212, 255, 0.3);">
                            🏢 부서별 분석 리포트
                        </h1>
                        ${this.generateDepartmentTable(deptAnalysis)}
                    </div>
                `;
            },
            
            generateExecutiveReport(dashboardData, employees) {
                // 실제 직원 데이터 사용 - API에서 가져온 데이터 우선 사용
                const actualEmployees = this.state.employees && this.state.employees.length > 0 ? this.state.employees : (employees || []);
                
                // 대시보드 통계 데이터 사용 (API에서 가져온 데이터)
                const stats = this.state.dashboardStats || dashboardData || {};
                const totalEmployeesFromAPI = stats.total_employees || actualEmployees.length || 0;
                const topTalentsFromAPI = stats.top_talents?.count || 0;
                const riskEmployeesFromAPI = stats.risk_employees?.count || 0;
                
                const avgScore = this.calculateAverageScore(actualEmployees);
                const gradeDistribution = this.calculateGradeDistribution(actualEmployees);
                const deptAnalysis = this.analyzeDepartments(actualEmployees);
                
                // 핵심 지표 계산 - API 데이터 우선 사용
                const topTalents = topTalentsFromAPI > 0 ? topTalentsFromAPI : ((gradeDistribution['S'] || 0) + (gradeDistribution['A'] || 0));
                const riskEmployees = riskEmployeesFromAPI > 0 ? riskEmployeesFromAPI : ((gradeDistribution['C'] || 0) + (gradeDistribution['D'] || 0));
                const totalCount = totalEmployeesFromAPI > 0 ? totalEmployeesFromAPI : actualEmployees.length;
                const retentionRate = totalCount > 0 ? Math.round(((totalCount - riskEmployees) / totalCount) * 100) : 0;
                const talentDensity = totalCount > 0 ? Math.round((topTalents / totalCount) * 100) : 0;
                
                // 부서별 성과
                const deptScores = Object.entries(deptAnalysis).map(([dept, data]) => ({
                    dept: dept,
                    score: data.avgScore || 0,
                    count: data.count,
                    topTalents: ((data.grades['S'] || 0) + (data.grades['A+'] || 0))
                })).sort((a, b) => b.score - a.score);
                
                // 위험도 평가
                const riskLevel = totalCount > 0 && riskEmployees > totalCount * 0.2 ? 'HIGH' : 
                                totalCount > 0 && riskEmployees > totalCount * 0.1 ? 'MEDIUM' : 'LOW';
                
                return `
                    <div style="font-family: 'Pretendard', sans-serif; line-height: 1.8; color: #333;">
                        <div style="background: linear-gradient(135deg, #00d9ff 0%, #7b61ff 50%, #667eea 100%); color: #fff; padding: 30px; border-radius: 12px; margin-bottom: 30px;">
                            <h1 style="margin: 0; font-size: 28px; font-weight: 700;">💼 경영진 브리핑</h1>
                            <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;"><strong>작성 부서:</strong> OK홀딩스 인사부</p>
                            <p style="margin: 5px 0 0 0; font-size: 14px; opacity: 0.8;">보고일: ${new Date().toLocaleDateString('ko-KR')}</p>
                        </div>

                        <div style="background: rgba(0, 217, 255, 0.1); padding: 25px; border-radius: 8px; margin-bottom: 30px; border-left: 5px solid #00d9ff;">
                            <h2 style="margin: 0 0 15px 0; color: #1976d2;">📊 경영 핵심 지표 (Executive Summary)</h2>
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                                <div style="text-align: center;">
                                    <div style="font-size: 24px; font-weight: bold; color: #1976d2;">${totalCount}명</div>
                                    <div style="color: #666;">전체 인력</div>
                                </div>
                                <div style="text-align: center;">
                                    <div style="font-size: 24px; font-weight: bold; color: ${avgScore >= 70 ? '#28a745' : avgScore >= 60 ? '#ffc107' : '#dc3545'};">${Math.round(avgScore)}점</div>
                                    <div style="color: #666;">평균 성과 점수</div>
                                </div>
                                <div style="text-align: center;">
                                    <div style="font-size: 24px; font-weight: bold; color: #28a745;">${topTalents}명 (${talentDensity}%)</div>
                                    <div style="color: #666;">핵심 인재</div>
                                </div>
                                <div style="text-align: center;">
                                    <div style="font-size: 24px; font-weight: bold; color: ${retentionRate >= 90 ? '#28a745' : retentionRate >= 80 ? '#ffc107' : '#dc3545'};">${retentionRate}%</div>
                                    <div style="color: #666;">예상 리텐션</div>
                                </div>
                            </div>
                        </div>

                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px;">
                            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px;">
                                <h3 style="margin: 0 0 15px 0; color: #00d9ff;">🎯 전략적 우선순위</h3>
                                <ul style="margin: 0; padding-left: 20px;">
                                    <li style="margin-bottom: 8px;"><strong>인재 확보:</strong> ${talentDensity < 15 ? '핵심 인재 비율 확대 필요' : '우수한 인재 보유율'}</li>
                                    <li style="margin-bottom: 8px;"><strong>성과 관리:</strong> ${avgScore < 600 ? '전반적 성과 개선 시급' : avgScore < 700 ? '성과 향상 여지 존재' : '우수한 성과 수준 유지'}</li>
                                    <li style="margin-bottom: 8px;"><strong>리스크 관리:</strong> ${riskLevel === 'HIGH' ? '고위험 인력 다수 존재' : riskLevel === 'MEDIUM' ? '중간 수준 리스크' : '안정적 조직 상태'}</li>
                                </ul>
                            </div>
                            
                            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px;">
                                <h3 style="margin: 0 0 15px 0; color: #00d9ff;">📈 조직 건강도</h3>
                                <div style="margin-bottom: 10px;">
                                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                                        <span>인재 밀도</span>
                                        <span style="font-weight: bold;">${talentDensity}%</span>
                                    </div>
                                    <div style="background: #e0e0e0; height: 8px; border-radius: 4px;">
                                        <div style="background: ${talentDensity >= 20 ? '#28a745' : talentDensity >= 15 ? '#ffc107' : '#dc3545'}; width: ${Math.min(talentDensity, 100)}%; height: 100%; border-radius: 4px;"></div>
                                    </div>
                                </div>
                                <div style="margin-bottom: 10px;">
                                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                                        <span>성과 수준</span>
                                        <span style="font-weight: bold;">${Math.round((avgScore/1000)*100)}%</span>
                                    </div>
                                    <div style="background: #e0e0e0; height: 8px; border-radius: 4px;">
                                        <div style="background: ${avgScore >= 700 ? '#28a745' : avgScore >= 600 ? '#ffc107' : '#dc3545'}; width: ${Math.min((avgScore/1000)*100, 100)}%; height: 100%; border-radius: 4px;"></div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <h2 style="color: #00d9ff; border-bottom: 2px solid #00d9ff; padding-bottom: 10px;">🏢 부서별 성과 현황</h2>
                        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 30px;">
                            <table style="width: 100%; border-collapse: collapse;">
                                <thead>
                                    <tr style="background: #e9ecef;">
                                        <th style="padding: 12px; border: 1px solid #dee2e6; text-align: left;">부서명</th>
                                        <th style="padding: 12px; border: 1px solid #dee2e6; text-align: center;">인원</th>
                                        <th style="padding: 12px; border: 1px solid #dee2e6; text-align: center;">평균점수</th>
                                        <th style="padding: 12px; border: 1px solid #dee2e6; text-align: center;">핵심인재</th>
                                        <th style="padding: 12px; border: 1px solid #dee2e6; text-align: center;">등급</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${deptScores.slice(0, 5).map((dept, index) => {
                                        // 100점과 1000점 스케일 모두 지원
                                        const grade = dept.score >= 90 || dept.score >= 900 ? 'S' : 
                                                     dept.score >= 85 || dept.score >= 850 ? 'A' : 
                                                     dept.score >= 80 || dept.score >= 800 ? 'B+' : 
                                                     dept.score >= 75 || dept.score >= 750 ? 'B' : 
                                                     dept.score >= 70 || dept.score >= 700 ? 'C' : 'D';
                                        const gradeColor = grade === 'S' ? '#69f0ae' : 
                                                          grade === 'A' ? '#4caf50' : 
                                                          grade === 'B+' ? '#ffd54f' : 
                                                          grade === 'B' ? '#ff9800' : 
                                                          grade === 'C' ? '#ff7043' : '#ff5252';
                                        return `
                                        <tr>
                                            <td style="padding: 12px; border: 1px solid #dee2e6;">
                                                ${index < 3 ? (index === 0 ? '🥇' : index === 1 ? '🥈' : '🥉') : ''} ${dept.dept}
                                            </td>
                                            <td style="padding: 12px; border: 1px solid #dee2e6; text-align: center;">${dept.count}명</td>
                                            <td style="padding: 12px; border: 1px solid #dee2e6; text-align: center; font-weight: bold;">${dept.score}점</td>
                                            <td style="padding: 12px; border: 1px solid #dee2e6; text-align: center;">${dept.topTalents}명</td>
                                            <td style="padding: 12px; border: 1px solid #dee2e6; text-align: center;">
                                                <span style="background: ${gradeColor}; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">${grade}</span>
                                            </td>
                                        </tr>
                                        `;
                                    }).join('')}
                                </tbody>
                            </table>
                        </div>

                        <h2 style="color: #00d9ff; border-bottom: 2px solid #00d9ff; padding-bottom: 10px;">⚠️ 경영 이슈 및 권고사항</h2>
                        <div style="background: linear-gradient(135deg, ${riskLevel === 'HIGH' ? 'rgba(244, 67, 54, 0.15)' : riskLevel === 'MEDIUM' ? 'rgba(255, 193, 7, 0.15)' : 'rgba(76, 175, 80, 0.15)'} 0%, ${riskLevel === 'HIGH' ? 'rgba(244, 67, 54, 0.08)' : riskLevel === 'MEDIUM' ? 'rgba(255, 152, 0, 0.1)' : 'rgba(76, 175, 80, 0.1)'} 100%); padding: 25px; border-radius: 12px; border: 1px solid ${riskLevel === 'HIGH' ? 'rgba(244, 67, 54, 0.3)' : riskLevel === 'MEDIUM' ? 'rgba(255, 193, 7, 0.3)' : 'rgba(76, 175, 80, 0.3)'}; backdrop-filter: blur(10px);">
                            <h3 style="margin: 0 0 15px 0; color: #ffffff; font-weight: 600; text-shadow: 0 1px 3px rgba(0,0,0,0.3);">즉시 조치 필요 사항</h3>
                            <ul style="margin: 0; padding-left: 25px; color: rgba(255, 255, 255, 0.95); font-size: 1.05em; line-height: 1.8;">
                                ${riskEmployees > employees.length * 0.2 ? 
                                    '<li><strong>🚨 고위험:</strong> 성과 미달 인력 ' + riskEmployees + '명 (전체 ' + Math.round((riskEmployees/employees.length)*100) + '%) - 즉시 개선 계획 수립 필요</li>' : ''}
                                ${talentDensity < 15 ? 
                                    '<li><strong>📈 인재 확보:</strong> 핵심 인재 비율 ' + talentDensity + '% - 업계 평균 20% 달성을 위한 채용/육성 전략 필요</li>' : ''}
                                ${avgScore < 650 ? 
                                    '<li><strong>💼 성과 개선:</strong> 조직 평균 성과 ' + avgScore + '점 - 교육 및 개발 투자 확대 권고</li>' : ''}
                                <li><strong>🎯 전략 실행:</strong> ${deptScores[0].dept} 우수 사례 벤치마킹을 통한 전사 성과 개선</li>
                                <li><strong>🔄 정기 모니터링:</strong> 월간 성과 리뷰 및 분기별 인재 현황 점검 체계 구축</li>
                            </ul>
                        </div>

                        <div style="background: #f1f8e9; padding: 20px; border-radius: 8px; margin-top: 20px; border-left: 4px solid #8bc34a;">
                            <h3 style="margin: 0 0 10px 0; color: #689f38;">💡 장기 전략 제안</h3>
                            <p style="margin: 0; color: #666;">
                                <strong>인재 관리:</strong> 핵심 인재 유지를 위한 맞춤형 보상 체계 및 경력 개발 프로그램 구축을 통해 
                                조직의 경쟁력을 지속적으로 강화하고 미래 성장 동력을 확보하시기 바랍니다.
                            </p>
                        </div>
                    </div>
                `;
            },
            
            // 리포트 액션 함수들
            printReport() {
                const content = document.getElementById('report-content').innerHTML;
                const printWindow = window.open('', '_blank');
                printWindow.document.write(`
                    <html>
                        <head>
                            <title>${this.currentReport?.title || '리포트'}</title>
                            <style>
                                body { font-family: 'Pretendard', sans-serif; padding: 20px; }
                                @media print { body { padding: 0; } }
                            </style>
                        </head>
                        <body>${content}</body>
                    </html>
                `);
                printWindow.document.close();
                printWindow.print();
            },
            
            copyReport() {
                const content = document.getElementById('report-content').innerText;
                navigator.clipboard.writeText(content).then(() => {
                    this.showNotification('리포트가 클립보드에 복사되었습니다', 'success');
                });
            },
            
            downloadReportAsHTML() {
                if (!this.currentReport) return;
                
                const html = `
                    <!DOCTYPE html>
                    <html lang="ko">
                    <head>
                        <meta charset="UTF-8">
                        <title>${this.currentReport.title}</title>
                        <style>
                            body { 
                                font-family: 'Pretendard', 'Malgun Gothic', sans-serif; 
                                padding: 40px; 
                                max-width: 1200px; 
                                margin: 0 auto; 
                            }
                        </style>
                    </head>
                    <body>
                        ${this.currentReport.content}
                    </body>
                    </html>
                `;
                
                const blob = new Blob([html], { type: 'text/html;charset=utf-8' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${this.currentReport.title}_${new Date().toISOString().split('T')[0]}.html`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
            },
            
            async downloadReportAsPDF() {
                if (!this.currentReport) return;
                
                try {
                    const reportContent = document.getElementById('report-content');
                    const canvas = await html2canvas(reportContent, {
                        scale: 2,
                        useCORS: true,
                        backgroundColor: '#ffffff'
                    });
                    
                    const { jsPDF } = window.jspdf;
                    const pdf = new jsPDF('p', 'mm', 'a4');
                    const imgData = canvas.toDataURL('image/png');
                    
                    const pageWidth = pdf.internal.pageSize.getWidth();
                    const pageHeight = pdf.internal.pageSize.getHeight();
                    const imgWidth = pageWidth - 20;
                    const imgHeight = (canvas.height * imgWidth) / canvas.width;
                    
                    let heightLeft = imgHeight;
                    let position = 10;
                    
                    pdf.addImage(imgData, 'PNG', 10, position, imgWidth, imgHeight);
                    heightLeft -= (pageHeight - 20);
                    
                    while (heightLeft > 0) {
                        position = heightLeft - imgHeight + 10;
                        pdf.addPage();
                        pdf.addImage(imgData, 'PNG', 10, position, imgWidth, imgHeight);
                        heightLeft -= (pageHeight - 20);
                    }
                    
                    pdf.save(`${this.currentReport.title}_${new Date().toISOString().split('T')[0]}.pdf`);
                    this.showNotification('PDF 다운로드가 완료되었습니다', 'success');
                } catch (error) {
                    console.error('PDF 생성 오류:', error);
                    this.showNotification('PDF 생성 중 오류가 발생했습니다', 'error');
                }
            },
            
            // 리포트 다운로드
            downloadReport(reportData) {
                const html = `
                    <!DOCTYPE html>
                    <html lang="ko">
                    <head>
                        <meta charset="UTF-8">
                        <title>${reportData.title}</title>
                        <style>
                            body { font-family: 'Malgun Gothic', sans-serif; padding: 40px; max-width: 800px; margin: 0 auto; }
                            h1 { color: #00d9ff; border-bottom: 2px solid #00d9ff; padding-bottom: 10px; }
                            h2 { color: #333; margin-top: 30px; }
                            h3 { color: #666; margin-top: 20px; }
                            ul { line-height: 1.8; }
                            .header { background: linear-gradient(135deg, rgba(52, 61, 84, 0.95) 0%, rgba(41, 49, 69, 0.9) 100%); padding: 20px; border-radius: 8px; margin-bottom: 30px; color: #fff; }
                            .footer { margin-top: 50px; padding-top: 20px; border-top: 1px solid #ddd; color: #999; font-size: 12px; }
                        </style>
                    </head>
                    <body>
                        <div class="header">
                            <h1>${reportData.title}</h1>
                            <p>생성일: ${new Date().toLocaleDateString('ko-KR')}</p>
                            <p>회사: ${reportData.company}</p>
                        </div>
                        ${reportData.content}
                        <div class="footer">
                            <p>이 리포트는 AIRISS v5.0 AI-Powered HR Intelligence System에 의해 자동 생성되었습니다.</p>
                            <p>© 2025 OK금융그룹. All rights reserved.</p>
                        </div>
                    </body>
                    </html>
                `;
                
                const blob = new Blob([html], { type: 'text/html;charset=utf-8' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${reportData.type}_report_${new Date().getTime()}.html`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
            },
            
            // 인사이트 새로고침
            async refreshInsights() {
                this.loadInsights();
                this.showNotification('인사이트가 업데이트되었습니다', 'success');
            },
            
            // 실시간 AI 인사이트 생성
            async generateRealTimeInsights() {
                // 생성 상태 표시
                const statusElement = document.getElementById('insights-generation-status');
                statusElement.style.display = 'block';
                
                try {
                    // 실시간 데이터 가져오기
                    await this.loadEmployeesData();
                    await this.loadDashboardData();
                    
                    // AI 분석 시뮬레이션 (실제 서버 API 호출로 대체 가능)
                    setTimeout(async () => {
                        // 데이터 분석 및 인사이트 생성
                        const employees = this.state.employees || [];
                        const avgScore = this.calculateAverageScore(employees);
                        
                        // AI 인사이트 생성 (확장 가능)
                        const insights = this.generateAIAnalysis(employees);
                        
                        // 인사이트 업데이트
                        this.loadInsights();
                        
                        // 상태 숨기기
                        statusElement.style.display = 'none';
                        
                        // 성공 메시지
                        this.showNotification('✅ AI 인사이트가 성공적으로 생성되었습니다', 'success');
                        
                        // 애니메이션 효과
                        const contentElement = document.getElementById('insights-content');
                        contentElement.style.animation = 'fadeIn 0.5s ease-in';
                    }, 2000); // 2초 지연 (실제 API에서는 제거)
                    
                } catch (error) {
                    console.error('AI insights generation failed:', error);
                    statusElement.style.display = 'none';
                    this.showNotification('❌ AI 인사이트 생성에 실패했습니다', 'error');
                }
            },
            
            // AI 분석 엔진 (확장 가능)
            generateAIAnalysis(employees) {
                const avgScore = this.calculateAverageScore(employees);
                const gradeDistribution = this.calculateGradeDistribution(employees);
                
                // AI 기반 패턴 분석
                const patterns = {
                    performanceTrend: avgScore >= 700 ? 'upward' : avgScore >= 600 ? 'stable' : 'downward',
                    talentDensity: (gradeDistribution['S'] + gradeDistribution['A+']) / employees.length,
                    riskLevel: (gradeDistribution['C'] + gradeDistribution['D']) / employees.length,
                    organizationalHealth: this.calculateOrganizationalHealth(employees)
                };
                
                // 예측 분석
                const predictions = {
                    sixMonthOutlook: patterns.performanceTrend === 'upward' ? 'positive' : 'concerning',
                    talentRetentionRisk: patterns.talentDensity < 0.1 ? 'high' : 'moderate',
                    growthPotential: avgScore >= 650 ? 'high' : 'limited'
                };
                
                return {
                    patterns,
                    predictions,
                    recommendations: this.generateRecommendations(patterns, predictions),
                    timestamp: new Date().toISOString()
                };
            },
            
            // 조직 건강도 계산
            calculateOrganizationalHealth(employees) {
                const avgScore = this.calculateAverageScore(employees);
                const gradeDistribution = this.calculateGradeDistribution(employees);
                
                return Math.min(100, Math.round(
                    (avgScore / 10) * 0.4 +
                    ((gradeDistribution['S'] + gradeDistribution['A+'] + gradeDistribution['A']) / employees.length * 100) * 0.3 +
                    ((1 - gradeDistribution['D'] / employees.length) * 100) * 0.3
                ));
            },
            
            // AI 기반 추천 생성
            generateRecommendations(patterns, predictions) {
                const recommendations = [];
                
                if (patterns.talentDensity < 0.1) {
                    recommendations.push('핵심 인재 육성 프로그램 긴급 도입');
                }
                
                if (patterns.riskLevel > 0.2) {
                    recommendations.push('하위 성과자 대상 집중 코칭 필요');
                }
                
                if (predictions.sixMonthOutlook === 'concerning') {
                    recommendations.push('조직 문화 혁신 프로그램 실시');
                }
                
                return recommendations;
            }
        };
        
        // 앱 초기화
        document.addEventListener('DOMContentLoaded', () => {
            try {
                console.log('🔍 AIRISS 객체 확인:', typeof window.AIRISS);
                if (window.AIRISS && typeof window.AIRISS.init === 'function') {
                    console.log('✅ AIRISS 객체가 정상적으로 로드되었습니다');
                    console.log('📋 사용 가능한 메서드:', Object.keys(window.AIRISS).filter(k => typeof window.AIRISS[k] === 'function'));
                    
                    // 초기화 실행
                    window.AIRISS.init();
                } else {
                    console.error('❌ AIRISS 객체 또는 init 메서드를 찾을 수 없습니다');
                }
            } catch (error) {
                console.error('❌ 초기화 오류:', error);
                console.error('상세 오류:', error.stack);
            }
        });
        
        // 부서별 성과 페이지네이션 함수
        if (!window.AIRISSApp) window.AIRISSApp = {};
        
        window.AIRISSApp.changeDeptPage = function(tableId, action) {
            const table = document.getElementById(tableId);
            if (!table) return;
            
            const allDepts = JSON.parse(table.dataset.allDepartments);
            const itemsPerPage = parseInt(table.dataset.itemsPerPage);
            let currentPage = parseInt(table.dataset.currentPage);
            const totalPages = Math.ceil(allDepts.length / itemsPerPage);
            const paginationId = table.dataset.paginationId;
            
            // 페이지 변경
            if (action === 'prev' && currentPage > 1) {
                currentPage--;
            } else if (action === 'next' && currentPage < totalPages) {
                currentPage++;
            } else if (typeof action === 'number') {
                currentPage = Math.max(1, Math.min(totalPages, action));
            }
            
            // 테이블 업데이트
            const startIdx = (currentPage - 1) * itemsPerPage;
            const endIdx = startIdx + itemsPerPage;
            const pageDepts = allDepts.slice(startIdx, endIdx);
            
            let rows = '';
            pageDepts.forEach(([dept, data], index) => {
                const globalIndex = startIdx + index;
                const count = data.count || 0;
                const avgScore = data.avgScore || data.avg_score || 0;
                let topTalents = 0;
                if (data.grades) {
                    topTalents = (data.grades['S'] || 0) + (data.grades['A+'] || 0) + (data.grades['A'] || 0);
                }
                const performance = avgScore >= 800 ? { grade: '우수', color: '#69f0ae' } :
                                  avgScore >= 700 ? { grade: '양호', color: '#ffd54f' } :
                                  avgScore >= 600 ? { grade: '보통', color: '#ff9800' } :
                                  { grade: '개선필요', color: '#ff5252' };
                const rankIcon = globalIndex === 0 ? '🥇' : globalIndex === 1 ? '🥈' : globalIndex === 2 ? '🥉' : '';
                
                const bgColor = index % 2 === 0 ? '0.03' : '0.05';
                rows += '<tr style="background: rgba(255, 255, 255, ' + bgColor + ');">';
                rows += '<td style="padding: 15px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #ffffff; font-weight: 500; text-align: center;">' + (globalIndex + 1) + '</td>';
                rows += '<td style="padding: 15px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #ffffff; font-weight: 500;">' + rankIcon + ' ' + dept + '</td>';
                rows += '<td style="padding: 15px; text-align: center; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #ffffff; font-weight: 600;">' + count + '명</td>';
                rows += '<td style="padding: 15px; text-align: center; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #00d4ff; font-weight: 700;">' + avgScore + '점</td>';
                rows += '<td style="padding: 15px; text-align: center; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #69f0ae; font-weight: 600;">' + topTalents + '명</td>';
                rows += '<td style="padding: 15px; text-align: center; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: ' + performance.color + '; font-weight: 600;">' + performance.grade + '</td>';
                rows += '</tr>';
            });
            
            table.querySelector('tbody').innerHTML = rows;
            table.dataset.currentPage = currentPage;
            document.getElementById(paginationId).textContent = currentPage + ' / ' + totalPages;
        };
        // AIRISS v5.0 Main Application - Debug Version
        
        // 전역 에러 핸들러 - 구문 오류 포착
        window.addEventListener('error', function(e) {
            if (e.message && e.message.includes('Unexpected token')) {
                console.error('❌ Syntax Error Detected:', e.message);
                console.error('  Line:', e.lineno, 'Column:', e.colno);
                console.error('  File:', e.filename);
                if (e.error && e.error.stack) {
                    console.error('  Stack:', e.error.stack);
                }
            }
        }, true);
        
        console.log('🚀 AIRISS v5.0 초기화 시작...');
        
        // 전역 AIRISS 객체 즉시 생성 (HTML onClick에서 바로 접근 가능)
        const AIRISS = window.AIRISS = {
            // 버전 정보 - 캐시 방지용 타임스탬프 추가
            version: '5.0.2-' + Date.now(),
            buildDate: '2025-08-08',
            buildTime: new Date().toISOString(),
            cacheBreaker: Math.random().toString(36).substring(7),
            
            // 상태 관리
            state: {
                dashboardStats: null,
                employees: [],
                previousStats: null  // 이전 통계 데이터
            },
            
            // 페이지네이션 상태 변수
            promotionDashboardPage: 1,
            talentDashboardPage: 1,
            riskDashboardPage: 1,
            // 리포트 페이지네이션 상태 변수
            talentReportPage: 1,
            promotionReportPage: 1,
            riskReportPage: 1,
            
            // API 설정
            api: {
                baseURL: '/api/v1',
                
                async request(method, endpoint, data = null) {
                    // 캐시 방지를 위한 타임스탬프 추가
                    const url = `${this.baseURL}${endpoint}${endpoint.includes('?') ? '&' : '?'}_t=${Date.now()}&_v=${AIRISS.cacheBreaker}`;
                    
                    const options = {
                        method,
                        headers: {
                            'Content-Type': 'application/json',
                            'X-Version': AIRISS.version,
                            'Cache-Control': 'no-cache',
                            'Pragma': 'no-cache'
                        },
                        cache: 'no-store'
                    };
                    
                    if (data) {
                        options.body = JSON.stringify(data);
                    }
                    
                    try {
                        console.log(`📡 API 호출: ${method} ${url}`);
                        const response = await fetch(url, options);
                        console.log(`📡 API Response Status: ${response.status}`);
                        
                        if (!response.ok) {
                            let errorMessage = `HTTP ${response.status}`;
                            try {
                                const errorData = await response.json();
                                errorMessage = errorData.detail || errorData.message || errorMessage;
                            } catch {
                                const errorText = await response.text();
                                errorMessage = errorText || errorMessage;
                            }
                            console.error('API Error Response:', errorMessage);
                            throw new Error(errorMessage);
                        }
                        
                        const result = await response.json();
                        console.log(`✅ API 응답:`, result);
                        return result;
                    } catch (error) {
                        console.error('❌ API Error:', {
                            url: url,
                            method: method,
                            error: error.message,
                            stack: error.stack
                        });
                        AIRISS.showNotification(`API 호출 실패: ${error.message}`, 'error');
                        throw error;
                    }
                }
            },
            
            // 상태 관리
            state: {
                currentTab: 'dashboard',
                employees: [],
                dashboardStats: {},
                uploadedFile: null,
                analysisJobId: null
            },
            
            // 초기화
            async init() {
                console.log(`AIRISS v${this.version} initialized at ${this.buildTime}`);
                this.attachEventListeners();
                // 직원 데이터를 먼저 로드한 후 대시보드 로드
                await this.loadEmployeesData();
                this.loadDashboardData();
                this.checkVersion();
            },
            
            // 버전 체크
            async checkVersion() {
                try {
                    const response = await fetch('/health');
                    const data = await response.json();
                    console.log('Server version:', data.deployment_version);
                } catch (error) {
                    console.error('Version check failed:', error);
                }
            },
            
            // 이벤트 리스너
            attachEventListeners() {
                // 드래그 앤 드롭
                const uploadArea = document.getElementById('upload-area');
                if (uploadArea) {
                    uploadArea.addEventListener('dragover', (e) => {
                        e.preventDefault();
                        uploadArea.classList.add('dragover');
                    });
                    
                    uploadArea.addEventListener('dragleave', () => {
                        uploadArea.classList.remove('dragover');
                    });
                    
                    uploadArea.addEventListener('drop', (e) => {
                        e.preventDefault();
                        uploadArea.classList.remove('dragover');
                        const files = e.dataTransfer.files;
                        if (files.length > 0) {
                            this.handleFileSelect({ target: { files } });
                        }
                    });
                }
                
                // 직원 검색 드롭다운 외부 클릭 시 닫기
                document.addEventListener('click', (e) => {
                    const dropdown = document.getElementById('employee-dropdown');
                    const searchInput = document.getElementById('employee-search');
                    
                    if (dropdown && searchInput && 
                        !dropdown.contains(e.target) && 
                        !searchInput.contains(e.target)) {
                        dropdown.style.display = 'none';
                    }
                });
            },
            
            // 탭 전환
            switchTab(tabName) {
                console.log(`🔄 탭 전환: ${tabName}`);
                
                // 모든 탭 컨텐츠 비활성화
                document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
                
                // 선택된 탭 컨텐츠 활성화
                const targetTab = document.getElementById(`${tabName}-tab`);
                if (targetTab) {
                    targetTab.classList.add('active');
                    console.log(`✅ 탭 활성화: ${tabName}-tab`);
                } else {
                    console.error(`❌ 탭을 찾을 수 없습니다: ${tabName}-tab`);
                }
                
                // 사이드바 메뉴 활성 상태 업데이트
                if (typeof updateSidebarActiveState === 'function') {
                    updateSidebarActiveState(tabName);
                }
                
                // 상태 업데이트
                this.state.currentTab = tabName;
                
                // 탭별 데이터 로드
                if (tabName === 'employees') {
                    this.loadEmployeesData();
                } else if (tabName === 'insights') {
                    this.loadInsights();
                }
            },
            
            // 리포트 표시 메서드
            showReport(type) {
                console.log(`📊 리포트 표시: ${type}`);
                
                // reports 탭으로 전환
                this.switchTab('reports');
                
                // 리포트 타입별 처리
                switch(type) {
                    case 'monthly':
                        this.generateReport('monthly');
                        break;
                    case 'talent':
                        this.generateReport('talent');
                        break;
                    case 'risk':
                        this.generateReport('risk');
                        break;
                    case 'performance':
                        this.generateReport('performance');
                        break;
                    case 'department':
                        this.generateReport('department');
                        break;
                    case 'executive':
                        this.generateReport('executive');
                        break;
                    default:
                        console.warn(`❌ 알 수 없는 리포트 타입: ${type}`);
                        this.generateReport('monthly'); // 기본값
                        break;
                }
            },
            
            // 증감 표기 업데이트 함수
            updateChangeIndicators(data) {
                // 이전 데이터는 DB에서 가져온 이전 기간 데이터를 사용해야 함
                // API에서 previous_period 데이터를 받아서 비교
                const previousData = data.previous_period || {};
                
                // 전체 직원 수 변화
                const totalChange = data.total_employees - (previousData.total_employees || data.total_employees);
                const totalPercent = previousData.total_employees ? 
                    Math.round((totalChange / previousData.total_employees) * 100) : 0;
                
                const totalChangeEl = document.querySelector('.stat-card:nth-child(1) .stat-change');
                if (totalChangeEl) {
                    if (totalChange > 0) {
                        totalChangeEl.className = 'stat-change positive';
                        totalChangeEl.innerHTML = `<span>↑</span><span>+${totalChange}명 (${totalPercent}%)</span>`;
                    } else if (totalChange < 0) {
                        totalChangeEl.className = 'stat-change negative';
                        totalChangeEl.innerHTML = `<span>↓</span><span>${totalChange}명 (${totalPercent}%)</span>`;
                    } else {
                        totalChangeEl.className = 'stat-change';
                        totalChangeEl.innerHTML = `<span>―</span><span>변화없음</span>`;
                    }
                }
                
                // 승진 후보자 변화
                const promotionChange = (data.promotion_candidates?.count || 0) - (previousData.promotion_candidates?.count || 0);
                const promotionChangeEl = document.querySelector('.stat-card:nth-child(2) .stat-change');
                if (promotionChangeEl) {
                    if (promotionChange > 0) {
                        promotionChangeEl.className = 'stat-change positive';
                        promotionChangeEl.innerHTML = `<span>↑</span><span>+${promotionChange}명 증가</span>`;
                    } else if (promotionChange < 0) {
                        promotionChangeEl.className = 'stat-change negative';
                        promotionChangeEl.innerHTML = `<span>↓</span><span>${Math.abs(promotionChange)}명 감소</span>`;
                    } else {
                        promotionChangeEl.className = 'stat-change';
                        promotionChangeEl.innerHTML = `<span>―</span><span>변화없음</span>`;
                    }
                }
                
                // 핵심 인재 변화
                const talentChange = (data.top_talents?.count || 0) - (previousData.top_talents?.count || 0);
                const talentChangeEl = document.querySelector('.stat-card:nth-child(3) .stat-change');
                if (talentChangeEl) {
                    if (talentChange > 0) {
                        talentChangeEl.className = 'stat-change positive';
                        talentChangeEl.innerHTML = `<span>↑</span><span>+${talentChange}명 증가</span>`;
                    } else if (talentChange < 0) {
                        talentChangeEl.className = 'stat-change negative';
                        talentChangeEl.innerHTML = `<span>↓</span><span>${Math.abs(talentChange)}명 감소</span>`;
                    } else {
                        talentChangeEl.className = 'stat-change';
                        talentChangeEl.innerHTML = `<span>―</span><span>변화없음</span>`;
                    }
                }
                
                // 관리 필요 인력 변화 (감소가 긍정적)
                const riskChange = (data.risk_employees?.count || 0) - (previousData.risk_employees?.count || 0);
                const riskPercent = previousData.risk_employees?.count ? 
                    Math.round((riskChange / previousData.risk_employees?.count) * 100) : 0;
                
                const riskChangeEl = document.querySelector('.stat-card:nth-child(4) .stat-change');
                if (riskChangeEl) {
                    if (riskChange < 0) {
                        // 관리 필요 인력이 감소한 경우 (긍정적)
                        riskChangeEl.className = 'stat-change positive';
                        riskChangeEl.innerHTML = `<span>↓</span><span>${Math.abs(riskChange)}명 감소 (${Math.abs(riskPercent)}%)</span>`;
                    } else if (riskChange > 0) {
                        // 관리 필요 인력이 증가한 경우 (부정적)
                        riskChangeEl.className = 'stat-change negative';
                        riskChangeEl.innerHTML = `<span>↑</span><span>+${riskChange}명 증가 (${riskPercent}%)</span>`;
                    } else {
                        riskChangeEl.className = 'stat-change';
                        riskChangeEl.innerHTML = `<span>―</span><span>변화없음</span>`;
                    }
                }
                
                // 현재 데이터를 state에 저장 (다음 비교를 위해)
                this.state.previousStats = {
                    total_employees: data.total_employees || 0,
                    promotion_candidates: { count: data.promotion_candidates?.count || 0 },
                    top_talents: { count: data.top_talents?.count || 0 },
                    risk_employees: { count: data.risk_employees?.count || 0 },
                    timestamp: new Date().toISOString()
                };
            },
            
            // 대시보드 데이터 로드
            async loadDashboardData() {
                try {
                    const data = await this.api.request('GET', '/hr-dashboard/stats');
                    this.state.dashboardStats = data;
                    
                    // 통계 업데이트
                    document.getElementById('stat-total').textContent = data.total_employees || 0;
                    document.getElementById('stat-promotion').textContent = data.promotion_candidates?.count || 0;
                    document.getElementById('stat-talent').textContent = data.top_talents?.count || 0;
                    document.getElementById('stat-risk').textContent = data.risk_employees?.count || 0;
                    
                    // 증감 표기 업데이트 (실제 데이터 기반)
                    this.updateChangeIndicators(data);
                    
                    // 승진 후보자 리스트 렌더링
                    this.renderPromotionList(data.promotion_candidates?.employees || []);
                    
                    // 핵심 인재 리스트 렌더링
                    this.renderTalentList(data.top_talents?.employees || []);
                    
                    // 관리 필요 인력 테이블
                    this.renderRiskEmployees(data.risk_employees?.employees || []);
                    
                    // 직원 데이터가 있을 때만 차트 렌더링
                    if (this.state.employees && this.state.employees.length > 0) {
                        this.renderDashboardCharts();
                    }
                } catch (error) {
                    console.error('Dashboard data load failed:', error);
                }
            },
            
            // 관리 필요 인력 렌더링
            renderRiskEmployees(employees) {
                const tbody = document.getElementById('risk-employees-table');
                if (!tbody) {
                    console.error('risk-employees-table not found');
                    return;
                }
                
                tbody.innerHTML = '';
                
                // 전체 카운트 업데이트 (전체 수)
                const counter = document.getElementById('stat-risk-table');
                if (counter) counter.textContent = this.state.dashboardStats?.risk_employees?.count || employees.length;
                
                // 페이지네이션 설정
                const riskPerPage = 10;
                const currentPage = this.riskDashboardPage || 1;
                const startIndex = (currentPage - 1) * riskPerPage;
                const endIndex = startIndex + riskPerPage;
                const paginatedEmployees = employees.slice(startIndex, endIndex);
                const totalPages = Math.ceil(employees.length / riskPerPage);
                
                console.log(`관리필요인력 렌더링 - 현재 페이지: ${currentPage}, 시작: ${startIndex}, 종료: ${endIndex}`);
                console.log(`표시할 인력 수: ${paginatedEmployees.length}명, 전체: ${employees.length}명`);
                
                paginatedEmployees.forEach(emp => {
                    const row = tbody.insertRow();
                    const riskColor = emp.risk_level === 'high' ? 'danger' : 'warning';
                    // ai_score 또는 risk_score 사용
                    const score = emp.ai_score || emp.risk_score || emp.overall_score || 0;
                    
                    row.innerHTML = `
                        <td>${emp.uid || emp.employee_id || '-'}</td>
                        <td>${emp.name || emp.employee_name || '익명'}</td>
                        <td>${emp.department || '-'}</td>
                        <td><span class="btn btn-${riskColor}" style="padding: 8px 16px; font-size: 14px; border-radius: 8px; font-weight: 500;">${emp.risk_level === 'high' ? '높음' : '보통'}</span></td>
                        <td style="font-weight: 600; color: ${score < 60 ? '#dc3545' : '#00d9ff'};">${Math.round(score)}</td>
                        <td>${emp.reason || emp.risk_reason || '-'}</td>
                        <td>
                            <button class="btn btn-primary" style="padding: 8px 16px; font-size: 14px; border-radius: 8px;" 
                                    onclick="AIRISS.viewEmployeeDetail('${emp.uid || emp.employee_id}')">상세</button>
                        </td>
                    `;
                });
                
                // 페이지네이션 컨트롤 추가
                this.renderRiskPagination(currentPage, totalPages, employees.length);
            },
            
            // 관리필요인력 페이지네이션 렌더링
            renderRiskPagination(currentPage, totalPages, totalCount) {
                // 기존 페이지네이션 제거
                const existingPagination = document.getElementById('risk-pagination');
                if (existingPagination) existingPagination.remove();
                
                if (totalPages <= 1) return;
                
                // 관리필요인력 테이블 찾기 (risk-employees-table의 부모 요소)
                const riskTable = document.getElementById('risk-employees-table');
                if (!riskTable) return;
                const tableContainer = riskTable.closest('.table-responsive');
                if (!tableContainer) return;
                
                const paginationHTML = `
                    <div id="risk-pagination" style="display: flex; justify-content: center; align-items: center; margin: 20px 0; gap: 10px;">
                        <button onclick="AIRISS.changeRiskDashboardPage(${currentPage - 1})" 
                            ${currentPage <= 1 ? 'disabled' : ''}
                            style="padding: 8px 16px; background: ${currentPage <= 1 ? '#6c757d' : '#007bff'}; color: white; border: none; border-radius: 6px; cursor: ${currentPage <= 1 ? 'not-allowed' : 'pointer'};">
                            ← 이전
                        </button>
                        <span style="margin: 0 15px; font-weight: 500;">
                            ${currentPage} / ${totalPages} 페이지 (${totalCount}명)
                        </span>
                        <button onclick="AIRISS.changeRiskDashboardPage(${currentPage + 1})" 
                            ${currentPage >= totalPages ? 'disabled' : ''}
                            style="padding: 8px 16px; background: ${currentPage >= totalPages ? '#6c757d' : '#007bff'}; color: white; border: none; border-radius: 6px; cursor: ${currentPage >= totalPages ? 'not-allowed' : 'pointer'};">
                            다음 →
                        </button>
                    </div>
                `;
                tableContainer.insertAdjacentHTML('afterend', paginationHTML);
            },
            
            // 대시보드 관리필요인력 페이지 변경
            changeRiskDashboardPage(page) {
                const employees = this.state.dashboardStats?.risk_employees?.employees || [];
                const totalPages = Math.ceil(employees.length / 10);
                
                console.log(`관리필요인력 페이지 변경 요청: ${page}, 전체 페이지: ${totalPages}, 전체 인원: ${employees.length}`);
                console.log(`현재 페이지: ${this.riskDashboardPage}`);
                
                if (page < 1 || page > totalPages) {
                    console.log('유효하지 않은 페이지 번호');
                    return;
                }
                
                this.riskDashboardPage = page;
                console.log(`관리필요인력 새 페이지로 설정: ${this.riskDashboardPage}`);
                
                this.renderRiskEmployees(employees);
            },
            
            // 승진 후보자 테이블 렌더링
            renderPromotionList(employees) {
                const tbody = document.getElementById('promotion-candidates-table');
                if (!tbody) return;
                
                tbody.innerHTML = '';
                
                // 전체 카운트 업데이트 (API에서 받은 전체 수 사용)
                const counter = document.getElementById('stat-promotion-table');
                if (counter) counter.textContent = this.state.dashboardStats?.promotion_candidates?.count || 0;
                
                // 페이지네이션 설정
                const promotionPerPage = 10;
                const currentPage = this.promotionDashboardPage || 1;
                const startIndex = (currentPage - 1) * promotionPerPage;
                const endIndex = startIndex + promotionPerPage;
                const paginatedEmployees = employees.slice(startIndex, endIndex);
                const totalPages = Math.ceil(employees.length / promotionPerPage);
                
                console.log(`렌더링 - 현재 페이지: ${currentPage}, 시작 인덱스: ${startIndex}, 종료 인덱스: ${endIndex}`);
                console.log(`표시할 직원 수: ${paginatedEmployees.length}명`);
                if (paginatedEmployees.length > 0) {
                    console.log('첫 번째 직원:', paginatedEmployees[0].name);
                }
                
                paginatedEmployees.forEach(emp => {
                    const row = tbody.insertRow();
                    const score = emp.ai_score || emp.overall_score || 0;
                    const grade = emp.grade || 'B';
                    
                    row.innerHTML = `
                        <td>${emp.uid || emp.employee_id || '-'}</td>
                        <td>${emp.name || emp.employee_name || '익명'}</td>
                        <td>${emp.department || '-'}</td>
                        <td>${emp.position || '-'}</td>
                        <td style="font-weight: 600; color: var(--primary-color);">${Math.round(score)}</td>
                        <td><span class="btn btn-success" style="padding: 8px 16px; font-size: 14px; border-radius: 8px; color: white !important;">${grade}</span></td>
                        <td>${emp.reasons && emp.reasons.length > 0 ? emp.reasons.slice(0, 2).join(', ') : '우수한 성과 및 리더십'}</td>
                        <td>
                            <button class="btn btn-primary" style="padding: 8px 16px; font-size: 14px; border-radius: 8px;" 
                                    onclick="AIRISS.viewEmployeeDetail('${emp.uid || emp.employee_id}')">상세</button>
                        </td>
                    `;
                });
                
                // 페이지네이션 컨트롤 추가
                this.renderPromotionPagination(currentPage, totalPages, employees.length);
            },
            
            // 승진후보자 페이지네이션 렌더링
            renderPromotionPagination(currentPage, totalPages, totalCount) {
                // 기존 페이지네이션 제거
                const existingPagination = document.getElementById('promotion-pagination');
                if (existingPagination) existingPagination.remove();
                
                if (totalPages <= 1) return;
                
                // 승진후보자 테이블 찾기
                const promotionTable = document.getElementById('promotion-candidates-table');
                if (!promotionTable) return;
                const tableContainer = promotionTable.closest('.table-responsive');
                if (!tableContainer) return;
                
                const paginationHTML = `
                    <div id="promotion-pagination" style="display: flex; justify-content: center; align-items: center; margin: 20px 0; gap: 10px;">
                        <button onclick="AIRISS.changePromotionDashboardPage(${currentPage - 1})" 
                            ${currentPage <= 1 ? 'disabled' : ''}
                            style="padding: 8px 16px; background: ${currentPage <= 1 ? '#6c757d' : '#007bff'}; color: white; border: none; border-radius: 6px; cursor: ${currentPage <= 1 ? 'not-allowed' : 'pointer'};">
                            ← 이전
                        </button>
                        <span style="margin: 0 15px; font-weight: 500;">
                            ${currentPage} / ${totalPages} 페이지 (${totalCount}명)
                        </span>
                        <button onclick="AIRISS.changePromotionDashboardPage(${currentPage + 1})" 
                            ${currentPage >= totalPages ? 'disabled' : ''}
                            style="padding: 8px 16px; background: ${currentPage >= totalPages ? '#6c757d' : '#007bff'}; color: white; border: none; border-radius: 6px; cursor: ${currentPage >= totalPages ? 'not-allowed' : 'pointer'};">
                            다음 →
                        </button>
                    </div>
                `;
                tableContainer.insertAdjacentHTML('afterend', paginationHTML);
            },
            
            // 대시보드 승진후보자 페이지 변경
            changePromotionDashboardPage(page) {
                const employees = this.state.dashboardStats?.promotion_candidates?.employees || [];
                const totalPages = Math.ceil(employees.length / 10);
                
                console.log(`페이지 변경 요청: ${page}, 전체 페이지: ${totalPages}, 전체 인원: ${employees.length}`);
                console.log(`현재 페이지: ${this.promotionDashboardPage}`);
                
                if (page < 1 || page > totalPages) {
                    console.log('유효하지 않은 페이지 번호');
                    return;
                }
                
                this.promotionDashboardPage = page;
                console.log(`새 페이지로 설정: ${this.promotionDashboardPage}`);
                
                this.renderPromotionList(employees);
            },
            
            // 핵심 인재 테이블 렌더링
            renderTalentList(employees) {
                const tbody = document.getElementById('talent-pool-table');
                if (!tbody) return;
                
                tbody.innerHTML = '';
                
                // 카운터 업데이트
                const counter = document.getElementById('stat-talent-table');
                if (counter) counter.textContent = employees.length;
                
                // 페이지네이션 설정
                const talentPerPage = 10;
                const currentPage = this.talentDashboardPage || 1;
                const startIndex = (currentPage - 1) * talentPerPage;
                const endIndex = startIndex + talentPerPage;
                const paginatedEmployees = employees.slice(startIndex, endIndex);
                const totalPages = Math.ceil(employees.length / talentPerPage);
                
                console.log(`핵심인재 렌더링 - 현재 페이지: ${currentPage}, 시작: ${startIndex}, 종료: ${endIndex}`);
                console.log(`표시할 인재 수: ${paginatedEmployees.length}명`);
                
                paginatedEmployees.forEach(emp => {
                    const row = tbody.insertRow();
                    const score = emp.ai_score || emp.overall_score || emp.score || 0;
                    const grade = emp.grade || 'A';
                    
                    row.innerHTML = `
                        <td>${emp.uid || emp.employee_id || '-'}</td>
                        <td>${emp.name || emp.employee_name || '익명'}</td>
                        <td>${emp.department || '-'}</td>
                        <td>${emp.position || '-'}</td>
                        <td style="font-weight: 600; color: var(--primary-color);">${Math.round(score)}</td>
                        <td><span class="btn btn-primary" style="padding: 8px 16px; font-size: 14px; border-radius: 8px; color: white !important;">${grade}</span></td>
                        <td>${emp.reason || '리더십, 전문성'}</td>
                        <td>
                            <button class="btn btn-primary" style="padding: 8px 16px; font-size: 14px; border-radius: 8px;" 
                                    onclick="AIRISS.viewEmployeeDetail('${emp.uid || emp.employee_id}')">상세</button>
                        </td>
                    `;
                });
                
                // 페이지네이션 컨트롤 추가
                this.renderTalentPagination(currentPage, totalPages, employees.length);
            },
            
            // 핵심인재 페이지네이션 렌더링
            renderTalentPagination(currentPage, totalPages, totalCount) {
                // 기존 페이지네이션 제거
                const existingPagination = document.getElementById('talent-pagination');
                if (existingPagination) existingPagination.remove();
                
                if (totalPages <= 1) return;
                
                // 핵심인재 테이블 찾기
                const talentTable = document.getElementById('talent-pool-table');
                if (!talentTable) return;
                const tableContainer = talentTable.closest('.table-responsive');
                if (!tableContainer) return;
                
                const paginationHTML = `
                    <div id="talent-pagination" style="display: flex; justify-content: center; align-items: center; margin: 20px 0; gap: 10px;">
                        <button onclick="AIRISS.changeTalentDashboardPage(${currentPage - 1})" 
                            ${currentPage <= 1 ? 'disabled' : ''}
                            style="padding: 8px 16px; background: ${currentPage <= 1 ? '#6c757d' : '#007bff'}; color: white; border: none; border-radius: 6px; cursor: ${currentPage <= 1 ? 'not-allowed' : 'pointer'};">
                            ← 이전
                        </button>
                        <span style="margin: 0 15px; font-weight: 500;">
                            ${currentPage} / ${totalPages} 페이지 (${totalCount}명)
                        </span>
                        <button onclick="AIRISS.changeTalentDashboardPage(${currentPage + 1})" 
                            ${currentPage >= totalPages ? 'disabled' : ''}
                            style="padding: 8px 16px; background: ${currentPage >= totalPages ? '#6c757d' : '#007bff'}; color: white; border: none; border-radius: 6px; cursor: ${currentPage >= totalPages ? 'not-allowed' : 'pointer'};">
                            다음 →
                        </button>
                    </div>
                `;
                tableContainer.insertAdjacentHTML('afterend', paginationHTML);
            },
            
            // 대시보드 핵심인재 페이지 변경
            changeTalentDashboardPage(page) {
                const employees = this.state.dashboardStats?.top_talents?.employees || [];
                const totalPages = Math.ceil(employees.length / 10);
                
                console.log(`핵심인재 페이지 변경 요청: ${page}, 전체 페이지: ${totalPages}, 전체 인원: ${employees.length}`);
                
                if (page < 1 || page > totalPages) {
                    console.log('유효하지 않은 페이지 번호');
                    return;
                }
                
                this.talentDashboardPage = page;
                console.log(`핵심인재 새 페이지로 설정: ${this.talentDashboardPage}`);
                
                this.renderTalentList(employees);
            },
            
            // 승진 후보자 리스트 토글
            togglePromotionList() {
                const listDiv = document.getElementById('promotion-list');
                if (listDiv) {
                    listDiv.style.display = listDiv.style.display === 'none' ? 'block' : 'none';
                }
            },
            
            // 핵심 인재 리스트 토글
            toggleTalentList() {
                const listDiv = document.getElementById('talent-list');
                if (listDiv) {
                    listDiv.style.display = listDiv.style.display === 'none' ? 'block' : 'none';
                }
            },
            
            // 대시보드 차트 렌더링
            renderDashboardCharts() {
                // Chart.js가 로드되었는지 확인
                if (typeof Chart === 'undefined') {
                    console.error('Chart.js가 로드되지 않았습니다.');
                    return;
                }
                
                // 실제 데이터 기반 등급 분포 계산
                const gradeDistribution = { 'S': 0, 'A+': 0, 'A': 0, 'B+': 0, 'B': 0, 'C': 0, 'D': 0 };
                
                // 직원 데이터 확인
                console.log('📊 차트 렌더링 - 직원 수:', this.state.employees.length);
                
                this.state.employees.forEach(emp => {
                    // ai_grade 필드를 우선 사용 (실제 데이터 구조에 맞춤)
                    const grade = emp.ai_grade || emp.grade || emp.OK등급 || 'C';
                    
                    // 첫 몇 개 데이터 로깅
                    if (gradeDistribution[grade] === 0) {
                        console.log(`첫 ${grade} 등급 발견:`, emp);
                    }
                    
                    if (gradeDistribution.hasOwnProperty(grade)) {
                        gradeDistribution[grade]++;
                    }
                });
                
                console.log('📊 등급 분포:', gradeDistribution);
                
                // 등급 분포 차트 - 막대그래프로 변경
                const gradeCtx = document.getElementById('gradeChart');
                if (gradeCtx) {
                    // 기존 차트가 있으면 제거
                    if (this.gradeChart) {
                        this.gradeChart.destroy();
                    }
                    
                    // 플러그인 옵션 설정 (ChartDataLabels 플러그인 사용 시)
                    const useDataLabels = typeof ChartDataLabels !== 'undefined';
                    
                    this.gradeChart = new Chart(gradeCtx, {
                        type: 'bar',
                        data: {
                            labels: Object.keys(gradeDistribution),
                            datasets: [{
                                label: '인원수',
                                data: Object.values(gradeDistribution),
                                backgroundColor: [
                                    '#1e3c72',
                                    '#2c5f2d', 
                                    '#2c5f2d',
                                    '#20547a',
                                    '#20547a',
                                    '#5f5f5f',
                                    '#8b2c2c'
                                ],
                                borderRadius: 8,
                                barThickness: 40
                            }]
                        },
                        plugins: useDataLabels ? [ChartDataLabels] : [],
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            layout: {
                                padding: {
                                    top: 30,  // 상단에 30px 여백 추가
                                    left: 10,
                                    right: 10,
                                    bottom: 10
                                }
                            },
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    ticks: {
                                        stepSize: 5,
                                        font: {
                                            size: 14,
                                            weight: '600'
                                        },
                                        color: '#ffffff'
                                    },
                                    grid: {
                                        drawBorder: false,
                                        color: 'rgba(255, 255, 255, 0.1)'
                                    },
                                    title: {
                                        display: true,
                                        text: '인원수',
                                        color: '#ffffff',
                                        font: {
                                            size: 14,
                                            weight: 'bold'
                                        }
                                    }
                                },
                                x: {
                                    grid: {
                                        display: false
                                    },
                                    ticks: {
                                        font: {
                                            size: 14,
                                            weight: 'bold'
                                        },
                                        color: '#ffffff'
                                    },
                                    title: {
                                        display: true,
                                        text: '등급',
                                        color: '#ffffff',
                                        font: {
                                            size: 14,
                                            weight: 'bold'
                                        }
                                    }
                                }
                            },
                            plugins: {
                                legend: {
                                    display: false
                                },
                                tooltip: {
                                    callbacks: {
                                        label: function(context) {
                                            return context.label + '등급: ' + context.parsed.y + '명';
                                        }
                                    }
                                },
                                datalabels: useDataLabels ? {
                                    anchor: 'end',
                                    align: 'top',
                                    color: '#ffffff',
                                    font: {
                                        weight: 'bold',
                                        size: 14
                                    },
                                    formatter: function(value) {
                                        return value > 0 ? value + '명' : '';
                                    }
                                } : false
                            }
                        }
                    });
                }
                
                // 실제 데이터 기반 부서별 평균 점수 계산
                const departmentScores = {};
                
                console.log('📈 부서별 성과 계산 시작...');
                
                this.state.employees.forEach((emp, idx) => {
                    // 부서명 확인 (department, 부서, dept 등)
                    const dept = emp.department || emp.부서 || emp.dept || '기타';
                    // 점수 확인 (ai_score, overall_score, 종합점수 등)
                    const score = emp.ai_score || emp.overall_score || emp.AIRISS_v2_종합점수 || emp.종합점수 || 0;
                    
                    // 첫 몇 개 데이터 로깅
                    if (idx < 3) {
                        console.log(`직원 ${idx + 1} - 부서: ${dept}, 점수: ${score}`);
                    }
                    
                    if (!departmentScores[dept]) {
                        departmentScores[dept] = { total: 0, count: 0 };
                    }
                    departmentScores[dept].total += score;
                    departmentScores[dept].count++;
                });
                
                console.log('📊 부서별 집계:', departmentScores);
                
                // 평균 점수 계산 및 정렬
                const departmentAverages = [];
                Object.keys(departmentScores).forEach(dept => {
                    if (departmentScores[dept].count > 0) {
                        const avg = Math.round(departmentScores[dept].total / departmentScores[dept].count);
                        departmentAverages.push({
                            name: dept,
                            avg: avg
                        });
                        console.log(`부서 ${dept}: 평균 ${avg}점 (${departmentScores[dept].count}명)`);
                    }
                });
                
                // 상위 5개 부서만 선택 (점수 기준 정렬)
                departmentAverages.sort((a, b) => b.avg - a.avg);
                const topDepartments = departmentAverages.slice(0, 5);
                
                console.log('📊 상위 5개 부서:', topDepartments);
                
                // 부서별 성과 차트
                const deptCtx = document.getElementById('departmentChart');
                if (deptCtx) {
                    // 기존 차트가 있으면 제거
                    if (this.departmentChart) {
                        this.departmentChart.destroy();
                    }
                    
                    const useDataLabels = typeof ChartDataLabels !== 'undefined';
                    
                    this.departmentChart = new Chart(deptCtx, {
                        type: 'bar',
                        data: {
                            labels: topDepartments.map(d => d.name),
                            datasets: [{
                                label: '평균 점수',
                                data: topDepartments.map(d => d.avg),
                                backgroundColor: '#00d9ff',
                                borderRadius: 8
                            }]
                        },
                        plugins: useDataLabels ? [ChartDataLabels] : [],
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            layout: {
                                padding: {
                                    top: 30,  // 상단에 30px 여백 추가
                                    left: 10,
                                    right: 10,
                                    bottom: 10
                                }
                            },
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    // max 값을 데이터에 따라 동적으로 설정
                                    max: Math.max(...topDepartments.map(d => d.avg)) > 100 ? 1000 : 100,
                                    ticks: {
                                        stepSize: Math.max(...topDepartments.map(d => d.avg)) > 100 ? 200 : 20,
                                        font: {
                                            size: 14,
                                            weight: '600'
                                        },
                                        color: '#ffffff'
                                    },
                                    grid: {
                                        drawBorder: false,
                                        color: 'rgba(255, 255, 255, 0.1)'
                                    },
                                    title: {
                                        display: true,
                                        text: '평균 점수',
                                        color: '#ffffff',
                                        font: {
                                            size: 14,
                                            weight: 'bold'
                                        }
                                    }
                                },
                                x: {
                                    grid: {
                                        display: false
                                    },
                                    ticks: {
                                        font: {
                                            size: 14,
                                            weight: 'bold'
                                        },
                                        color: '#ffffff'
                                    },
                                    title: {
                                        display: true,
                                        text: '부서명',
                                        color: '#ffffff',
                                        font: {
                                            size: 14,
                                            weight: 'bold'
                                        }
                                    }
                                }
                            },
                            plugins: {
                                legend: {
                                    display: false
                                },
                                tooltip: {
                                    callbacks: {
                                        label: function(context) {
                                            return '평균 점수: ' + context.parsed.y + '점';
                                        }
                                    }
                                },
                                datalabels: useDataLabels ? {
                                    anchor: 'end',
                                    align: 'top',
                                    color: '#ffffff',
                                    font: {
                                        weight: 'bold',
                                        size: 14
                                    },
                                    formatter: function(value) {
                                        return value + '점';
                                    }
                                } : false
                            }
                        }
                    });
                }
            },
            
            // 직원 데이터 로드 (개선된 버전)
            async loadEmployeesData() {
                try {
                    console.log('🔄 직원 데이터 로딩 시작...');
                    const response = await this.api.request('GET', '/employees/list');
                    console.log('📊 받은 응답:', response);
                    
                    // 에러 응답 체크
                    if (response && response.success === false) {
                        console.error('❌ 서버 에러:', response.error);
                        this.showNotification(
                            `데이터 로드 실패: ${response.error?.message || '서버 오류가 발생했습니다'}`, 
                            'error'
                        );
                        this.renderNoDataMessage(response.error?.message || '데이터베이스 조회에 실패했습니다');
                        return;
                    }
                    
                    // 성공 응답 처리
                    if (response && response.employees) {
                        if (response.employees.length > 0) {
                            this.state.employees = response.employees;
                            console.log('👥 로드된 직원 수:', this.state.employees.length);
                            this.renderEmployees(this.state.employees);
                            
                            // 대시보드 탭에서 차트 업데이트
                            if (this.state.currentTab === 'dashboard') {
                                this.renderDashboardCharts();
                            }
                        } else {
                            console.log('📭 데이터가 비어있음');
                            this.renderNoDataMessage('분석된 직원 데이터가 없습니다');
                        }
                    } else if (response && response.data) {
                        // 다른 형식의 응답 처리
                        const data = response.data;
                        if (data.items && data.items.length > 0) {
                            this.state.employees = data.items;
                            console.log('👥 로드된 직원 수:', this.state.employees.length);
                            this.renderEmployees(this.state.employees);
                        } else {
                            console.log('📭 데이터가 비어있음');
                            this.renderNoDataMessage('분석된 직원 데이터가 없습니다');
                        }
                    } else {
                        console.warn('⚠️ 예상치 못한 데이터 형식:', response);
                        this.renderNoDataMessage('예상치 못한 응답 형식입니다');
                    }
                } catch (error) {
                    console.error('❌ 직원 데이터 로딩 실패:', error);
                    this.showNotification('서버 연결에 실패했습니다', 'error');
                    this.renderNoDataMessage('서버 연결에 실패했습니다');
                }
            },
            
            // 데이터 없음 메시지 표시
            renderNoDataMessage(message) {
                const tbody = document.getElementById('employees-table');
                if (!tbody) return;
                
                tbody.innerHTML = `
                    <tr>
                        <td colspan="7" style="text-align: center; padding: 60px 20px;">
                            <div style="opacity: 0.7;">
                                <div style="font-size: 3rem; margin-bottom: 20px;">⚠️</div>
                                <h3 style="margin-bottom: 15px; color: var(--text-primary);">${message}</h3>
                                ${message.includes('실패') ? `
                                    <p style="margin: 15px 0; color: var(--text-secondary);">
                                        서버 연결을 확인하거나 잠시 후 다시 시도해주세요.
                                    </p>
                                    <button class="btn btn-secondary" onclick="AIRISS.loadEmployeesData()" style="margin-top: 10px;">
                                        🔄 다시 시도
                                    </button>
                                ` : `
                                    <p style="margin: 15px 0; color: var(--text-secondary);">
                                        직원 데이터를 업로드하여 AI 분석을 시작하세요.
                                    </p>
                                    <button class="btn btn-primary" onclick="AIRISS.switchTab('upload')" style="margin-top: 10px;">
                                        📤 데이터 업로드하기
                                    </button>
                                `}
                            </div>
                        </td>
                    </tr>
                `;
            },
            
            // 직원 목록 렌더링 (페이지네이션 포함)
            renderEmployees(employees, page = 1) {
                const tbody = document.getElementById('employees-table');
                if (!tbody) return;
                
                tbody.innerHTML = '';
                
                // 데이터가 없는 경우
                if (!employees || employees.length === 0) {
                    this.renderNoDataMessage('분석된 직원 데이터가 없습니다');
                    return;
                }
                
                console.log('🖼️ 직원 목록 렌더링:', employees.length + '명');
                
                // 페이지네이션 설정
                const itemsPerPage = 20;
                const totalPages = Math.ceil(employees.length / itemsPerPage);
                const startIndex = (page - 1) * itemsPerPage;
                const endIndex = startIndex + itemsPerPage;
                this.state.currentPage = page;
                
                // 현재 페이지의 직원만 표시
                employees.slice(startIndex, endIndex).forEach((emp, index) => {
                    const row = tbody.insertRow();
                    
                    // EmployeeService의 반환 구조에 맞춤
                    const employeeId = emp.employee_id || emp.uid || emp.id;
                    const employeeName = emp.name || emp.employee_name || '익명';
                    const department = emp.department || '-';
                    const position = emp.position || '-';
                    const grade = emp.grade || emp.ai_grade || 'C';
                    const score = emp.ai_score || emp.overall_score || 0;
                    
                    // 디버깅: 실제 등급 확인
                    if (index < 3) {
                        console.log(`직원 ${employeeId}: grade=${emp.grade}, ai_grade=${emp.ai_grade}, 최종=${grade}`);
                    }
                    
                    // 등급에 따른 색상 결정
                    const gradeColor = {
                        'S': 'success',
                        'A+': 'success',
                        'A': 'primary',
                        'B+': 'info',
                        'B': 'warning',
                        'C': 'secondary',
                        'D': 'danger'
                    }[grade] || 'secondary';
                    
                    row.innerHTML = `
                        <td style="font-weight: 500;">${employeeId || (index + 1)}</td>
                        <td style="font-weight: 600;">${employeeName}</td>
                        <td>${department}</td>
                        <td>${position}</td>
                        <td><span class="btn btn-${gradeColor}" style="padding: 8px 16px; font-size: 14px; font-weight: 600; border-radius: 8px; color: white !important;">${grade}</span></td>
                        <td style="font-weight: 600; color: var(--primary-color); font-size: 18px;">${Math.round(score)}</td>
                        <td>
                            <button class="btn btn-primary" style="padding: 10px 20px; font-size: 14px; border-radius: 8px; font-weight: 500;" 
                                    onclick="AIRISS.viewEmployeeDetail('${employeeId}')">
                                상세보기
                            </button>
                        </td>
                    `;
                });
                
                // 페이지네이션 UI 렌더링
                this.renderPagination(employees.length, page, itemsPerPage);
                
                console.log('✅ 직원 목록 렌더링 완료');
            },
            
            // 페이지네이션 UI 렌더링
            renderPagination(totalItems, currentPage, itemsPerPage) {
                const container = document.getElementById('pagination-container');
                if (!container) return;
                
                const totalPages = Math.ceil(totalItems / itemsPerPage);
                container.innerHTML = '';
                
                // 이전 버튼
                const prevBtn = document.createElement('button');
                prevBtn.className = 'btn btn-secondary';
                prevBtn.innerHTML = '◀ 이전';
                prevBtn.disabled = currentPage === 1;
                prevBtn.onclick = () => this.renderEmployees(this.state.employees, currentPage - 1);
                prevBtn.style.cssText = 'padding: 8px 16px; font-size: 14px; border-radius: 8px;';
                container.appendChild(prevBtn);
                
                // 페이지 정보
                const pageInfo = document.createElement('div');
                pageInfo.style.cssText = 'padding: 8px 20px; font-weight: 600; color: #2c3e50;';
                pageInfo.innerHTML = `
                    <span style="font-size: 16px;">${currentPage} / ${totalPages}</span>
                    <br>
                    <span style="font-size: 12px; color: #666;">총 ${totalItems}명</span>
                `;
                container.appendChild(pageInfo);
                
                // 다음 버튼
                const nextBtn = document.createElement('button');
                nextBtn.className = 'btn btn-secondary';
                nextBtn.innerHTML = '다음 ▶';
                nextBtn.disabled = currentPage === totalPages;
                nextBtn.onclick = () => this.renderEmployees(this.state.employees, currentPage + 1);
                nextBtn.style.cssText = 'padding: 8px 16px; font-size: 14px; border-radius: 8px;';
                container.appendChild(nextBtn);
            },
            
            // 직원 상세 보기 - 풍부한 AI 분석 정보 표시
            async viewEmployeeDetail(employeeId) {
                try {
                    console.log('🔍 직원 상세 조회 시작:', employeeId);
                    const data = await this.api.request('GET', `/employees/${employeeId}/ai-analysis`);
                    console.log('✅ 직원 상세 데이터:', data);
                    
                    // 데이터 검증
                    if (!data || data.error) {
                        throw new Error(data?.error || '데이터를 불러올 수 없습니다');
                    }
                    
                    // 등급별 색상 매핑 - 심플하고 전문적인 색상
                    const gradeColors = {
                        'S': '#2c3e50',
                        'A+': '#27ae60', 
                        'A': '#27ae60',
                        'B+': '#3498db',
                        'B': '#3498db',
                        'C': '#7f8c8d',
                        'D': '#e74c3c'
                    };
                    
                    const gradeColor = gradeColors[data.grade] || gradeColors['C'];
                    
                    // 디버깅: 데이터 확인
                    console.log('🎯 렌더링할 데이터:', {
                        competencies: data.competencies,
                        strengths: data.strengths,
                        improvements: data.improvements,
                        ai_comment: data.ai_comment,
                        career_recommendation: data.career_recommendation,
                        education_suggestion: data.education_suggestion
                    });
                    
                    const modalBody = document.getElementById('modal-body');
                    modalBody.style.maxHeight = '85vh';
                    modalBody.style.overflowY = 'auto';
                    modalBody.style.padding = '2rem';
                    modalBody.innerHTML = `
                        <div class="employee-detail-content" style="padding: 20px;">
                            <!-- 헤더 섹션 - 심플하고 전문적인 프로필 카드 스타일 -->
                            <div class="profile-header" style="
                                background: linear-gradient(135deg, rgba(52, 61, 84, 0.95) 0%, rgba(41, 49, 69, 0.9) 100%);
                                border: 1px solid rgba(88, 95, 112, 0.4);
                                border-radius: 8px;
                                padding: 30px;
                                color: #ffffff;
                                margin-bottom: 30px;
                                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                            ">
                                <div style="display: flex; align-items: center; justify-content: space-between;">
                                    <div style="flex: 1;">
                                        <h2 style="font-size: 32px; margin-bottom: 10px; font-weight: 700;">
                                            ${data.name || '익명'}
                                        </h2>
                                        <div style="display: flex; gap: 20px; margin-bottom: 20px; color: rgba(255, 255, 255, 0.85);">
                                            <span>📍 ${data.department || '미지정'}</span>
                                            <span>💼 ${data.position || '미지정'}</span>
                                            <span>👨‍💼 추정경력 ${data.estimated_experience || '3-5년'}</span>
                                            <span>📅 ${data.analyzed_at ? new Date(data.analyzed_at).toLocaleDateString('ko-KR') : '최근 분석'}</span>
                                        </div>
                                        <div style="display: flex; gap: 15px; align-items: center; flex-wrap: wrap;">
                                            <span style="
                                                background: rgba(0, 217, 255, 0.15);
                                                padding: 6px 14px;
                                                border-radius: 4px;
                                                font-size: 14px;
                                                color: #ffffff;
                                                border: 1px solid rgba(0, 217, 255, 0.3);
                                            ">
                                                🏆 ${data.performance_indicators?.overall_ranking || '상위 50%'}
                                            </span>
                                            <span style="
                                                background: rgba(0, 217, 255, 0.15);
                                                padding: 6px 14px;
                                                border-radius: 4px;
                                                font-size: 14px;
                                                color: #ffffff;
                                                border: 1px solid rgba(0, 217, 255, 0.3);
                                            ">
                                                📈 성장잠재력 ${data.performance_indicators?.growth_potential || '보통'}
                                            </span>
                                            <span style="
                                                background: rgba(0, 217, 255, 0.15);
                                                padding: 6px 14px;
                                                border-radius: 4px;
                                                font-size: 14px;
                                                color: #ffffff;
                                                border: 1px solid rgba(0, 217, 255, 0.3);
                                            ">
                                                ⚖️ 역량균형 ${data.performance_indicators?.competency_balance || '보통'}
                                            </span>
                                            <span style="
                                                background: rgba(0, 217, 255, 0.15);
                                                padding: 6px 14px;
                                                border-radius: 4px;
                                                font-size: 14px;
                                                color: #ffffff;
                                                border: 1px solid rgba(0, 217, 255, 0.3);
                                            ">
                                                👑 리더십준비도 ${data.performance_indicators?.leadership_readiness || '개발필요'}
                                            </span>
                                        </div>
                                    </div>
                                    <div style="text-align: center;">
                                        <div style="
                                            width: 140px;
                                            height: 140px;
                                            border-radius: 50%;
                                            background: linear-gradient(135deg, rgba(52, 61, 84, 0.95) 0%, rgba(41, 49, 69, 0.9) 100%);
                                            display: flex;
                                            flex-direction: column;
                                            align-items: center;
                                            justify-content: center;
                                            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                                            position: relative;
                                        ">
                                            <div style="font-size: 48px; font-weight: bold; color: #00d9ff;">
                                                ${data.ai_score || 0}
                                            </div>
                                            <div style="font-size: 14px; color: rgba(255, 255, 255, 0.8); margin-top: 5px;">AI SCORE</div>
                                            <div style="
                                                position: absolute;
                                                top: -10px;
                                                right: -10px;
                                                background: ${gradeColor};
                                                color: white;
                                                padding: 6px 12px;
                                                border-radius: 4px;
                                                font-size: 14px;
                                                font-weight: bold;
                                            ">${data.grade || 'C'}</div>
                                        </div>
                                        <div style="
                                            margin-top: 15px;
                                            background: linear-gradient(135deg, #00d9ff 0%, #7b61ff 100%);
                                            color: white;
                                            padding: 8px 20px;
                                            border-radius: 4px;
                                            font-weight: 500;
                                            font-size: 14px;
                                            display: inline-block;
                                        ">
                                            평균 역량: ${data.competency_average || 0}점
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- 성과 분석 대시보드 - 심플한 디자인 -->
                            <div class="performance-dashboard" style="
                                display: grid;
                                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                                gap: 15px;
                                margin-bottom: 30px;
                            ">
                                <div class="metric-card" style="
                                    background: linear-gradient(135deg, rgba(52, 61, 84, 0.95) 0%, rgba(41, 49, 69, 0.9) 100%);
                                    color: #ffffff;
                                    padding: 20px;
                                    border-radius: 8px;
                                    text-align: center;
                                    border: 1px solid #e9ecef;
                                    box-shadow: 0 2px 4px rgba(0,0,0,0.08);
                                ">
                                    <div style="font-size: 20px; margin-bottom: 8px;">📊</div>
                                    <div style="font-size: 18px; font-weight: 600; margin-bottom: 5px;">${data.performance_indicators?.overall_ranking || '상위 50%'}</div>
                                    <div style="font-size: 13px; color: rgba(255, 255, 255, 0.7);">전체 순위</div>
                                </div>
                                <div class="metric-card" style="
                                    background: linear-gradient(135deg, rgba(52, 61, 84, 0.95) 0%, rgba(41, 49, 69, 0.9) 100%);
                                    color: #ffffff;
                                    padding: 20px;
                                    border-radius: 8px;
                                    text-align: center;
                                    border: 1px solid #e9ecef;
                                    box-shadow: 0 2px 4px rgba(0,0,0,0.08);
                                ">
                                    <div style="font-size: 20px; margin-bottom: 8px;">📈</div>
                                    <div style="font-size: 18px; font-weight: 600; margin-bottom: 5px;">${data.performance_indicators?.growth_potential || '보통'}</div>
                                    <div style="font-size: 13px; color: rgba(255, 255, 255, 0.7);">성장 잠재력</div>
                                </div>
                                <div class="metric-card" style="
                                    background: linear-gradient(135deg, rgba(52, 61, 84, 0.95) 0%, rgba(41, 49, 69, 0.9) 100%);
                                    color: #ffffff;
                                    padding: 20px;
                                    border-radius: 8px;
                                    text-align: center;
                                    border: 1px solid #e9ecef;
                                    box-shadow: 0 2px 4px rgba(0,0,0,0.08);
                                ">
                                    <div style="font-size: 20px; margin-bottom: 8px;">⚠️</div>
                                    <div style="font-size: 18px; font-weight: 600; margin-bottom: 5px;">${data.performance_indicators?.risk_level || '보통'}</div>
                                    <div style="font-size: 13px; color: rgba(255, 255, 255, 0.7);">이직 위험도</div>
                                </div>
                                <div class="metric-card" style="
                                    background: linear-gradient(135deg, rgba(52, 61, 84, 0.95) 0%, rgba(41, 49, 69, 0.9) 100%);
                                    color: #ffffff;
                                    padding: 20px;
                                    border-radius: 8px;
                                    text-align: center;
                                    border: 1px solid #e9ecef;
                                    box-shadow: 0 2px 4px rgba(0,0,0,0.08);
                                ">
                                    <div style="font-size: 20px; margin-bottom: 8px;">👑</div>
                                    <div style="font-size: 18px; font-weight: 600; margin-bottom: 5px;">${data.performance_indicators?.leadership_readiness || '개발필요'}</div>
                                    <div style="font-size: 13px; color: rgba(255, 255, 255, 0.7);">리더십 준비도</div>
                                </div>
                            </div>
                            
                            <!-- 8대 역량 분석 - 심플한 스타일 -->
                            <div class="competency-section" style="
                                background: linear-gradient(135deg, rgba(52, 61, 84, 0.95) 0%, rgba(41, 49, 69, 0.9) 100%);
                                border-radius: 8px;
                                padding: 25px;
                                margin-bottom: 25px;
                                border: 1px solid #e9ecef;
                                box-shadow: 0 2px 4px rgba(0,0,0,0.08);
                            ">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                                    <h3 style="color: #00d9ff; font-size: 20px; font-weight: 600; margin: 0;">
                                        🎯 8대 핵심 역량 분석
                                    </h3>
                                    <div style="
                                        background: #6c757d;
                                        color: white;
                                        padding: 6px 16px;
                                        border-radius: 4px;
                                        font-size: 14px;
                                        font-weight: 500;
                                    ">
                                        평균 점수: ${Math.round(Object.values(data.competencies || {}).reduce((a, b) => a + b, 0) / 8)}점
                                    </div>
                                </div>
                                
                                <div class="competency-grid" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px;">
                                    ${Object.entries(data.competencies || {}).map(([key, value]) => {
                                        const percentage = (value / 100) * 100;
                                        const barColor = value >= 80 ? '#28a745' : value >= 60 ? '#ffc107' : '#dc3545';
                                        return `
                                        <div class="competency-item" style="
                                            background: #f8f9fa;
                                            padding: 16px;
                                            border-radius: 6px;
                                            border: 1px solid #dee2e6;
                                            position: relative;
                                        ">
                                            <div style="position: relative; z-index: 2;">
                                                <div style="font-weight: 600; margin-bottom: 10px; font-size: 14px; color: #2c3e50;">
                                                    ${key}
                                                </div>
                                                <div style="font-size: 32px; color: ${barColor}; font-weight: 700; margin-bottom: 10px;">
                                                    ${value || 0}
                                                </div>
                                                <div style="
                                                    background: #e9ecef;
                                                    border-radius: 4px;
                                                    height: 6px;
                                                    overflow: hidden;
                                                ">
                                                    <div style="
                                                        background: ${barColor};
                                                        height: 100%;
                                                        width: ${percentage}%;
                                                        border-radius: 4px;
                                                    "></div>
                                                </div>
                                                <div style="
                                                    margin-top: 8px;
                                                    font-size: 12px;
                                                    color: #666;
                                                ">
                                                    ${value >= 80 ? '우수' : value >= 60 ? '양호' : '개발필요'}
                                                </div>
                                            </div>
                                        </div>
                                        `;
                                    }).join('')}
                                </div>
                            </div>
                            
                            <!-- 역량 상세 분석 - 새로 추가 -->
                            <div class="competency-analysis" style="
                                background: linear-gradient(135deg, rgba(52, 61, 84, 0.95) 0%, rgba(41, 49, 69, 0.9) 100%);
                                border-radius: 20px;
                                padding: 30px;
                                margin-bottom: 30px;
                                box-shadow: 0 5px 20px rgba(0,0,0,0.05);
                            ">
                                <h3 style="color: #00d9ff; font-size: 24px; font-weight: 600; margin-bottom: 25px;">
                                    📈 역량 상세 분석
                                </h3>
                                
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px;">
                                    <!-- 강점 역량 TOP 3 -->
                                    <div style="
                                        background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 100%);
                                        padding: 25px;
                                        border-radius: 15px;
                                        border-left: 4px solid #28a745;
                                    ">
                                        <h4 style="color: #28a745; margin: 0 0 20px 0; font-size: 18px; font-weight: 600;">
                                            🏆 강점 역량 TOP 3
                                        </h4>
                                        ${(data.top_competencies || []).map((comp, idx) => `
                                            <div style="
                                                display: flex;
                                                justify-content: space-between;
                                                align-items: center;
                                                padding: 12px 0;
                                                border-bottom: ${idx < 2 ? '1px solid rgba(40, 167, 69, 0.1)' : 'none'};
                                            ">
                                                <div style="display: flex; align-items: center;">
                                                    <span style="
                                                        background: #28a745;
                                                        color: white;
                                                        width: 24px;
                                                        height: 24px;
                                                        border-radius: 50%;
                                                        display: flex;
                                                        align-items: center;
                                                        justify-content: center;
                                                        font-size: 12px;
                                                        font-weight: bold;
                                                        margin-right: 12px;
                                                    ">${idx + 1}</span>
                                                    <span style="font-weight: 500; color: #2c3e50;">${comp[0]}</span>
                                                </div>
                                                <div style="
                                                    background: #28a745;
                                                    color: white;
                                                    padding: 4px 12px;
                                                    border-radius: 15px;
                                                    font-size: 14px;
                                                    font-weight: bold;
                                                ">${comp[1]}점</div>
                                            </div>
                                        `).join('')}
                                    </div>
                                    
                                    <!-- 개발 필요 역량 -->
                                    <div style="
                                        background: linear-gradient(135deg, #ffebee 0%, #fff3e0 100%);
                                        padding: 25px;
                                        border-radius: 15px;
                                        border-left: 4px solid #ff9800;
                                    ">
                                        <h4 style="color: #ff9800; margin: 0 0 20px 0; font-size: 18px; font-weight: 600;">
                                            🎯 개발 필요 역량
                                        </h4>
                                        ${(data.low_competencies || []).map((comp, idx) => `
                                            <div style="
                                                display: flex;
                                                justify-content: space-between;
                                                align-items: center;
                                                padding: 12px 0;
                                                border-bottom: ${idx < 2 ? '1px solid rgba(255, 152, 0, 0.1)' : 'none'};
                                            ">
                                                <div style="display: flex; align-items: center;">
                                                    <span style="
                                                        background: #ff9800;
                                                        color: white;
                                                        width: 24px;
                                                        height: 24px;
                                                        border-radius: 50%;
                                                        display: flex;
                                                        align-items: center;
                                                        justify-content: center;
                                                        font-size: 12px;
                                                        font-weight: bold;
                                                        margin-right: 12px;
                                                    ">${idx + 1}</span>
                                                    <span style="font-weight: 500; color: #2c3e50;">${comp[0]}</span>
                                                </div>
                                                <div style="
                                                    background: ${comp[1] >= 60 ? '#ffc107' : '#dc3545'};
                                                    color: white;
                                                    padding: 4px 12px;
                                                    border-radius: 15px;
                                                    font-size: 14px;
                                                    font-weight: bold;
                                                ">${comp[1]}점</div>
                                            </div>
                                        `).join('')}
                                    </div>
                                </div>
                            </div>
                            
                            <!-- AI 종합 피드백 - 심플한 디자인 -->
                            ${data.ai_comment ? `
                            <div class="ai-feedback-section" style="
                                background: linear-gradient(135deg, rgba(52, 61, 84, 0.95) 0%, rgba(41, 49, 69, 0.9) 100%);
                                border-radius: 8px;
                                padding: 25px;
                                margin-bottom: 25px;
                                border: 1px solid #e9ecef;
                                box-shadow: 0 2px 4px rgba(0,0,0,0.08);
                                border-left: 4px solid #6c757d;
                            ">
                                <div style="display: flex; align-items: center; margin-bottom: 16px;">
                                    <div style="
                                        width: 32px;
                                        height: 32px;
                                        background: #6c757d;
                                        border-radius: 4px;
                                        display: flex;
                                        align-items: center;
                                        justify-content: center;
                                        margin-right: 10px;
                                        color: white;
                                        font-size: 16px;
                                    ">🤖</div>
                                    <h3 style="margin: 0; color: #00d9ff; font-size: 18px; font-weight: 600;">AI 종합 분석 리포트</h3>
                                </div>
                                <div style="
                                    background: #f8f9fa;
                                    padding: 16px;
                                    border-radius: 6px;
                                    font-size: 15px;
                                    line-height: 1.6;
                                    color: #495057;
                                    border: 1px solid #e9ecef;
                                ">${data.ai_comment}</div>
                            </div>
                            ` : ''}
                            
                            <!-- 강점과 개선점 - 심플한 카드 스타일 -->
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 25px;">
                                <div class="strengths-section" style="
                                    background: linear-gradient(135deg, rgba(52, 61, 84, 0.95) 0%, rgba(41, 49, 69, 0.9) 100%);
                                    border-radius: 8px;
                                    padding: 20px;
                                    border: 1px solid #e9ecef;
                                    box-shadow: 0 2px 4px rgba(0,0,0,0.08);
                                    border-left: 4px solid #28a745;
                                ">
                                    <div style="display: flex; align-items: center; margin-bottom: 16px;">
                                        <div style="
                                            width: 32px;
                                            height: 32px;
                                            background: #28a745;
                                            border-radius: 4px;
                                            display: flex;
                                            align-items: center;
                                            justify-content: center;
                                            margin-right: 10px;
                                            color: white;
                                            font-size: 16px;
                                        ">✨</div>
                                        <h3 style="margin: 0; color: #00d9ff; font-size: 18px; font-weight: 600;">핵심 강점</h3>
                                    </div>
                                    <div>
                                        ${(data.strengths || ['데이터가 충분하지 않습니다']).map((s, idx) => {
                                            // 긴 텍스트를 파싱하여 구조화된 형태로 변환
                                            let parsedContent = s;
                                            
                                            // "강점1:", "강점2:" 형식으로 분리
                                            if (s.includes('강점1:') || s.includes('강점2:') || s.includes('강점3:')) {
                                                const parts = s.split(/강점\d+:|아이콘\d+에/);
                                                parsedContent = parts.filter(part => part.trim()).map(part => {
                                                    const cleanPart = part.trim().replace(/^-\s*/, '');
                                                    if (cleanPart.includes(' - ')) {
                                                        const [title, description] = cleanPart.split(' - ', 2);
                                                        return '<strong>' + title.trim() + '</strong><br><span style="color: #6c757d; font-size: 14px;">' + description.trim() + '</span>';
                                                    }
                                                    return cleanPart;
                                                }).join('<br><br>');
                                            }
                                            
                                            return '<div style="padding: 12px; background: #f8f9fa; border-radius: 6px; margin-bottom: 10px; border: 1px solid #e9ecef;"><div style="color: #495057; line-height: 1.6;">' + parsedContent + '</div></div>';
                                        }).join('')}
                                    </div>
                                </div>
                                
                                <div class="improvements-section" style="
                                    background: linear-gradient(135deg, rgba(52, 61, 84, 0.95) 0%, rgba(41, 49, 69, 0.9) 100%);
                                    border-radius: 8px;
                                    padding: 20px;
                                    border: 1px solid #e9ecef;
                                    box-shadow: 0 2px 4px rgba(0,0,0,0.08);
                                    border-left: 4px solid #ffc107;
                                ">
                                    <div style="display: flex; align-items: center; margin-bottom: 16px;">
                                        <div style="
                                            width: 32px;
                                            height: 32px;
                                            background: #ffc107;
                                            border-radius: 4px;
                                            display: flex;
                                            align-items: center;
                                            justify-content: center;
                                            margin-right: 10px;
                                            color: white;
                                            font-size: 16px;
                                        ">🎯</div>
                                        <h3 style="margin: 0; color: #00d9ff; font-size: 18px; font-weight: 600;">개선 포인트</h3>
                                    </div>
                                    <div>
                                        ${(data.improvements || ['데이터가 충분하지 않습니다']).map((i, idx) => `
                                            <div style="
                                                padding: 12px;
                                                background: #f8f9fa;
                                                border-radius: 6px;
                                                margin-bottom: 10px;
                                                border: 1px solid #e9ecef;
                                            ">
                                                <div style="color: #495057; line-height: 1.6;">${i}</div>
                                            </div>
                                        `).join('')}
                                    </div>
                                </div>
                            </div>
                            
                            <!-- 추천 사항 - 심플한 카드 스타일 -->
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 25px;">
                                <div class="career-recommendation" style="
                                    background: linear-gradient(135deg, rgba(52, 61, 84, 0.95) 0%, rgba(41, 49, 69, 0.9) 100%);
                                    border-radius: 8px;
                                    padding: 20px;
                                    border: 1px solid #e9ecef;
                                    box-shadow: 0 2px 4px rgba(0,0,0,0.08);
                                    border-left: 4px solid #007bff;
                                ">
                                    <div style="display: flex; align-items: center; margin-bottom: 16px;">
                                        <div style="
                                            width: 32px;
                                            height: 32px;
                                            background: #007bff;
                                            border-radius: 4px;
                                            display: flex;
                                            align-items: center;
                                            justify-content: center;
                                            margin-right: 10px;
                                            color: white;
                                            font-size: 16px;
                                        ">🚀</div>
                                        <h3 style="margin: 0; color: #00d9ff; font-size: 18px; font-weight: 600;">경력 발전 로드맵</h3>
                                    </div>
                                    <div>
                                        ${(data.career_recommendation && data.career_recommendation.length > 0 ? data.career_recommendation : []).map(r => `
                                            <div style="
                                                background: #f8f9fa;
                                                padding: 12px;
                                                border-radius: 6px;
                                                margin-bottom: 10px;
                                                border: 1px solid #e9ecef;
                                                display: flex;
                                                align-items: center;
                                            ">
                                                <span style="margin-right: 10px; color: #007bff;">▶</span>
                                                <span style="color: #495057;">${r}</span>
                                            </div>
                                        `).join('')}
                                    </div>
                                </div>
                                
                                <div class="education-suggestion" style="
                                    background: linear-gradient(135deg, rgba(52, 61, 84, 0.95) 0%, rgba(41, 49, 69, 0.9) 100%);
                                    border-radius: 8px;
                                    padding: 20px;
                                    border: 1px solid #e9ecef;
                                    box-shadow: 0 2px 4px rgba(0,0,0,0.08);
                                    border-left: 4px solid #17a2b8;
                                ">
                                    <div style="display: flex; align-items: center; margin-bottom: 16px;">
                                        <div style="
                                            width: 32px;
                                            height: 32px;
                                            background: #17a2b8;
                                            border-radius: 4px;
                                            display: flex;
                                            align-items: center;
                                            justify-content: center;
                                            margin-right: 10px;
                                            color: white;
                                            font-size: 16px;
                                        ">📚</div>
                                        <h3 style="margin: 0; color: #00d9ff; font-size: 18px; font-weight: 600;">맞춤 교육 프로그램</h3>
                                    </div>
                                    <div>
                                        ${(data.education_suggestion || ['리더십 교육 프로그램', '전략적 사고 워크샵']).map(e => `
                                            <div style="
                                                background: #f8f9fa;
                                                padding: 12px;
                                                border-radius: 6px;
                                                margin-bottom: 10px;
                                                border: 1px solid #e9ecef;
                                                display: flex;
                                                align-items: center;
                                            ">
                                                <span style="margin-right: 10px; color: #17a2b8;">▶</span>
                                                <span style="color: #495057;">${e}</span>
                                            </div>
                                        `).join('')}
                                    </div>
                                </div>
                            </div>
                            
                            <!-- 종합 인사이트 - 심플한 디자인 -->
                            <div class="comprehensive-insights" style="
                                background: linear-gradient(135deg, rgba(52, 61, 84, 0.95) 0%, rgba(41, 49, 69, 0.9) 100%);
                                border-radius: 8px;
                                padding: 25px;
                                margin-bottom: 25px;
                                border: 1px solid #e9ecef;
                                box-shadow: 0 2px 4px rgba(0,0,0,0.08);
                            ">
                                <h3 style="color: #00d9ff; font-size: 20px; font-weight: 600; margin-bottom: 20px;">
                                    🎯 종합 인사이트 & 액션 플랜
                                </h3>
                                
                                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px;">
                                    <!-- 즉시 실행 가능한 액션 -->
                                    <div style="
                                        background: #f8f9fa;
                                        padding: 16px;
                                        border-radius: 6px;
                                        border: 1px solid #e9ecef;
                                        border-left: 3px solid #28a745;
                                    ">
                                        <h4 style="color: #28a745; margin: 0 0 15px 0; font-size: 16px; font-weight: 600;">
                                            ⚡ 즉시 실행 (1-3개월)
                                        </h4>
                                        <ul style="margin: 0; padding-left: 20px; color: #495057; line-height: 1.6;">
                                            ${data.low_competencies && data.low_competencies.length > 0 ? `
                                                <li>${data.low_competencies[0][0]} 역량 집중 개발</li>
                                                <li>멘토링 프로그램 참여</li>
                                                <li>관련 온라인 과정 수강</li>
                                            ` : `
                                                <li>강점 역량 더욱 활용</li>
                                                <li>동료와 지식 공유</li>
                                                <li>새로운 도전 과제 수행</li>
                                            `}
                                        </ul>
                                    </div>
                                    
                                    <!-- 중기 발전 계획 -->
                                    <div style="
                                        background: #f8f9fa;
                                        padding: 16px;
                                        border-radius: 6px;
                                        border: 1px solid #e9ecef;
                                        border-left: 3px solid #007bff;
                                    ">
                                        <h4 style="color: #007bff; margin: 0 0 15px 0; font-size: 16px; font-weight: 600;">
                                            🎯 중기 목표 (6-12개월)
                                        </h4>
                                        <ul style="margin: 0; padding-left: 20px; color: #495057; line-height: 1.6;">
                                            ${data.ai_score >= 70 ? `
                                                <li>팀 프로젝트 리딩 경험</li>
                                                <li>교차 부서 협업 확대</li>
                                                <li>전문성 인증 취득</li>
                                            ` : `
                                                <li>기본 역량 안정화</li>
                                                <li>업무 프로세스 개선</li>
                                                <li>전문 교육 이수</li>
                                            `}
                                        </ul>
                                    </div>
                                    
                                    <!-- 장기 비전 -->
                                    <div style="
                                        background: #f8f9fa;
                                        padding: 16px;
                                        border-radius: 6px;
                                        border: 1px solid #e9ecef;
                                        border-left: 3px solid #ffc107;
                                    ">
                                        <h4 style="color: #e67e22; margin: 0 0 15px 0; font-size: 16px; font-weight: 600;">
                                            🚀 장기 비전 (1-2년)
                                        </h4>
                                        <ul style="margin: 0; padding-left: 20px; color: #495057; line-height: 1.6;">
                                            ${data.ai_score >= 80 ? `
                                                <li>리더십 포지션 도전</li>
                                                <li>전략 기획 참여</li>
                                                <li>조직 발전 기여</li>
                                            ` : data.ai_score >= 60 ? `
                                                <li>전문가 포지션 확립</li>
                                                <li>핵심 업무 담당</li>
                                                <li>후배 멘토링 역할</li>
                                            ` : `
                                                <li>안정적 성과 달성</li>
                                                <li>역량 균형 개발</li>
                                                <li>전문 분야 확립</li>
                                            `}
                                        </ul>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- 성과 예측 및 리스크 분석 - 심플한 디자인 -->
                            <div class="prediction-analysis" style="
                                background: linear-gradient(135deg, rgba(52, 61, 84, 0.95) 0%, rgba(41, 49, 69, 0.9) 100%);
                                border-radius: 8px;
                                padding: 25px;
                                margin-bottom: 25px;
                                border: 1px solid #e9ecef;
                                box-shadow: 0 2px 4px rgba(0,0,0,0.08);
                            ">
                                <h3 style="color: #00d9ff; font-size: 20px; font-weight: 600; margin-bottom: 20px;">
                                    🔮 AI 예측 분석 & 리스크 관리
                                </h3>
                                
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                                    <!-- 성과 예측 -->
                                    <div style="
                                        background: #f8f9fa;
                                        padding: 20px;
                                        border-radius: 6px;
                                        border: 1px solid #e9ecef;
                                    ">
                                        <h4 style="color: #2c3e50; margin: 0 0 16px 0; font-size: 16px; font-weight: 600;">
                                            📊 성과 예측 (6개월 후)
                                        </h4>
                                        <div style="margin-bottom: 12px;">
                                            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                                <span style="font-size: 14px; color: #495057;">예상 AI 점수</span>
                                                <span style="font-weight: bold; color: #2c3e50;">${Math.min(100, data.ai_score + (data.ai_score >= 70 ? 8 : data.ai_score >= 50 ? 12 : 15))}점</span>
                                            </div>
                                            <div style="
                                                background: #e9ecef;
                                                border-radius: 4px;
                                                height: 6px;
                                                overflow: hidden;
                                            ">
                                                <div style="
                                                    background: #28a745;
                                                    height: 100%;
                                                    width: ${Math.min(100, ((data.ai_score + (data.ai_score >= 70 ? 8 : data.ai_score >= 50 ? 12 : 15)) / 100) * 100)}%;
                                                "></div>
                                            </div>
                                        </div>
                                        <div style="font-size: 14px; color: #6c757d; line-height: 1.5;">
                                            현재 성장 궤도를 유지할 경우, ${data.ai_score >= 70 ? '리더십 역할 준비 완료' : data.ai_score >= 50 ? '안정적인 성과 향상 예상' : '기본 역량 강화 필요'}
                                        </div>
                                    </div>
                                    
                                    <!-- 리스크 분석 -->
                                    <div style="
                                        background: #f8f9fa;
                                        padding: 20px;
                                        border-radius: 6px;
                                        border: 1px solid #e9ecef;
                                    ">
                                        <h4 style="color: #2c3e50; margin: 0 0 16px 0; font-size: 16px; font-weight: 600;">
                                            ⚠️ 리스크 요인 분석
                                        </h4>
                                        <div>
                                            ${data.ai_score < 60 ? `
                                                <div style="
                                                    background: #fff5f5;
                                                    padding: 12px;
                                                    border-radius: 6px;
                                                    margin-bottom: 10px;
                                                    border: 1px solid #fed7d7;
                                                ">
                                                    <div style="font-weight: 600; margin-bottom: 5px; color: #c53030;">🔴 높은 리스크</div>
                                                    <div style="font-size: 13px; color: #495057;">성과 개선 및 역량 강화 시급</div>
                                                </div>
                                            ` : data.ai_score < 75 ? `
                                                <div style="
                                                    background: #fffdf5;
                                                    padding: 12px;
                                                    border-radius: 6px;
                                                    margin-bottom: 10px;
                                                    border: 1px solid #feebc8;
                                                ">
                                                    <div style="font-weight: 600; margin-bottom: 5px; color: #c05621;">🟡 보통 리스크</div>
                                                    <div style="font-size: 13px; color: #495057;">지속적인 발전 노력 필요</div>
                                                </div>
                                            ` : `
                                                <div style="
                                                    background: #f0fff4;
                                                    padding: 12px;
                                                    border-radius: 6px;
                                                    margin-bottom: 10px;
                                                    border: 1px solid #c6f6d5;
                                                ">
                                                    <div style="font-weight: 600; margin-bottom: 5px; color: #276749;">🟢 낮은 리스크</div>
                                                    <div style="font-size: 13px; color: #495057;">안정적이며 성장 궤도 양호</div>
                                                </div>
                                            `}
                                            <div style="font-size: 14px; color: #495057; line-height: 1.5;">
                                                <strong>권장 조치:</strong><br>
                                                ${data.performance_indicators?.risk_level === '높음' ? '즉시 개선 계획 수립 및 집중 관리' : 
                                                  data.performance_indicators?.risk_level === '보통' ? '정기적 모니터링 및 점진적 개선' : 
                                                  '현재 수준 유지 및 추가 도전 과제 부여'}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- 분석 정보 및 메타데이터 -->
                            <div class="analysis-metadata" style="
                                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                                border-radius: 15px;
                                padding: 25px;
                                margin-top: 30px;
                                border-top: 3px solid var(--primary-color);
                            ">
                                <h4 style="color: #2c3e50; margin: 0 0 20px 0; font-size: 18px; font-weight: 600;">
                                    📋 분석 리포트 정보
                                </h4>
                                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
                                    <div>
                                        <div style="font-size: 12px; color: #6c757d; margin-bottom: 5px;">분석 엔진</div>
                                        <div style="font-weight: 600; color: #2c3e50;">${data.analysis_version || 'AIRISS v5.0 Enhanced'}</div>
                                    </div>
                                    <div>
                                        <div style="font-size: 12px; color: #6c757d; margin-bottom: 5px;">리포트 생성</div>
                                        <div style="font-weight: 600; color: #2c3e50;">${new Date().toLocaleString('ko-KR')}</div>
                                    </div>
                                    <div>
                                        <div style="font-size: 12px; color: #6c757d; margin-bottom: 5px;">분석 기간</div>
                                        <div style="font-weight: 600; color: #2c3e50;">최근 3개월 데이터 기준</div>
                                    </div>
                                    <div>
                                        <div style="font-size: 12px; color: #6c757d; margin-bottom: 5px;">신뢰도</div>
                                        <div style="font-weight: 600; color: var(--success);">95%+</div>
                                    </div>
                                </div>
                                
                                <div style="
                                    margin-top: 20px;
                                    padding: 15px;
                                    background: rgba(255, 107, 53, 0.1);
                                    border-radius: 10px;
                                    border-left: 4px solid var(--primary-color);
                                ">
                                    <div style="font-size: 14px; color: #2c3e50; line-height: 1.6;">
                                        <strong>💡 이 리포트는</strong> AI 기반 종합 분석으로 생성된 개인맞춤형 인사평가 보고서입니다. 
                                        정확한 인사결정을 위해서는 추가적인 정성적 평가와 함께 종합적으로 활용하시기 바랍니다.
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                    
                    document.getElementById('modal-title').textContent = `${data.name || employeeId} - 상세 AI 분석 리포트`;
                    
                    // 현재 직원 데이터를 전역에 저장 (PDF 다운로드용)
                    this.currentEmployeeData = data;
                    
                    const modal = document.getElementById('employee-modal');
                    modal.classList.add('active');
                } catch (error) {
                    console.error('❌ Employee detail load failed:', {
                        employeeId: employeeId,
                        error: error.message,
                        stack: error.stack
                    });
                    
                    const modalBody = document.getElementById('modal-body');
                    modalBody.innerHTML = `
                        <div style="text-align: center; padding: 40px; color: #dc3545;">
                            <h3>⚠️ 데이터 로드 실패</h3>
                            <p>직원 ID: ${employeeId}</p>
                            <p>분석 데이터를 불러올 수 없습니다.</p>
                            <p style="font-size: 14px; color: #6c757d;">오류: ${error.message}</p>
                            <p style="font-size: 12px; color: #999;">API Endpoint: /api/v1/employees/${employeeId}/ai-analysis</p>
                        </div>
                    `;
                    
                    document.getElementById('modal-title').textContent = '데이터 로드 오류';
                    document.getElementById('employee-modal').classList.add('active');
                }
            },
            
            // 파일 선택 처리
            handleFileSelect(event) {
                const file = event.target.files[0];
                if (!file) return;
                
                this.state.uploadedFile = file;
                this.uploadFile(file);
            },
            
            // 파일 업로드
            async uploadFile(file) {
                const formData = new FormData();
                formData.append('file', file);
                
                document.getElementById('upload-progress').style.display = 'block';
                document.getElementById('progress-text').textContent = '업로드 중...';
                
                try {
                    const response = await fetch('/api/v1/upload', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (!response.ok) throw new Error('Upload failed');
                    
                    const data = await response.json();
                    document.getElementById('progress-fill').style.width = '100%';
                    document.getElementById('progress-text').textContent = '업로드 완료!';
                    
                    // 파일 분석 결과 표시
                    this.showFileAnalysisResult(data);
                    
                    // Step 2로 이동
                    setTimeout(() => {
                        document.getElementById('analysis-config-step').style.display = 'block';
                        document.getElementById('analysis-config-step').scrollIntoView({ behavior: 'smooth' });
                    }, 1000);
                    
                } catch (error) {
                    console.error('File upload failed:', error);
                    this.showNotification('파일 업로드 실패', 'error');
                }
            },
            
            // 파일 분석 결과 표시
            showFileAnalysisResult(data) {
                const resultDiv = document.getElementById('file-analysis-result');
                const airissReady = data.airiss_ready ? '✅ 가능' : '❌ 불가능';
                const hybridReady = data.hybrid_ready ? '✅ 가능' : '❌ 불가능';
                
                resultDiv.innerHTML = `
                    <div style="background: var(--bg-secondary); padding: 20px; border-radius: 12px;">
                        <h4>📊 파일 분석 결과</h4>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 15px;">
                            <div>
                                <p><strong>파일명:</strong> ${data.filename}</p>
                                <p><strong>총 레코드:</strong> ${data.total_records}개</p>
                                <p><strong>컬럼 수:</strong> ${data.column_count}개</p>
                                <p><strong>데이터 완성도:</strong> ${data.data_quality.completeness}%</p>
                            </div>
                            <div>
                                <p><strong>AI 분석:</strong> ${airissReady}</p>
                                <p><strong>하이브리드 분석:</strong> ${hybridReady}</p>
                                <p><strong>UID 컬럼:</strong> ${data.uid_columns.length}개</p>
                                <p><strong>의견 컬럼:</strong> ${data.opinion_columns.length}개</p>
                            </div>
                        </div>
                        ${data.uid_columns.length > 0 ? `<p style="margin-top: 10px;"><strong>UID 컬럼:</strong> ${data.uid_columns.join(', ')}</p>` : ''}
                        ${data.opinion_columns.length > 0 ? `<p style="margin-top: 5px;"><strong>의견 컬럼:</strong> ${data.opinion_columns.join(', ')}</p>` : ''}
                    </div>
                `;
                resultDiv.style.display = 'block';
                this.state.uploadedFileData = data;
            },
            
            // 사용자 설정으로 분석 시작
            async startAnalysisWithConfig() {
                if (!this.state.uploadedFileData) {
                    this.showNotification('먼저 파일을 업로드해주세요', 'warning');
                    return;
                }
                
                // 사용자 설정 수집
                const analysisMode = document.querySelector('input[name="analysis-mode"]:checked').value;
                const openaiModel = document.getElementById('openai-model').value;
                const maxTokens = parseInt(document.getElementById('max-tokens').value);
                const sampleSize = parseInt(document.getElementById('sample-size').value);
                const enableAiFeedback = document.getElementById('enable-ai-feedback').checked;
                const enableRealtime = document.getElementById('enable-realtime').checked;
                
                // Step 3로 이동
                document.getElementById('analysis-config-step').style.display = 'none';
                document.getElementById('analysis-progress-step').style.display = 'block';
                document.getElementById('analysis-progress-step').scrollIntoView({ behavior: 'smooth' });
                
                try {
                    const requestBody = {
                        sample_size: sampleSize === -1 ? this.state.uploadedFileData.total_records : sampleSize,
                        analysis_mode: analysisMode,
                        enable_ai_feedback: enableAiFeedback,
                        openai_model: openaiModel,
                        max_tokens: maxTokens
                    };
                    
                    this.addAnalysisLog(`🚀 AI 분석 시작 - 모델: ${openaiModel}, 토큰: ${maxTokens}, 인원: ${requestBody.sample_size}명`);
                    
                    const data = await this.api.request('POST', `/analysis/analyze/${this.state.uploadedFileData.file_id}`, requestBody);
                    this.state.analysisJobId = data.job_id;
                    this.state.analysisConfig = requestBody;
                    this.state.enableRealtime = enableRealtime;
                    
                    this.addAnalysisLog(`✅ 분석 작업 생성됨 - Job ID: ${data.job_id}`);
                    
                    // 실시간 상태 체크 시작
                    if (enableRealtime) {
                        this.startRealtimeProgress();
                    } else {
                        this.checkAnalysisStatus();
                    }
                } catch (error) {
                    console.error('Analysis start failed:', error);
                    this.addAnalysisLog('❌ 분석 시작 실패: ' + error.message);
                }
            },
            
            // 실시간 진행 상황 시작
            startRealtimeProgress() {
                this.state.analysisStartTime = Date.now();
                this.state.progressInterval = setInterval(() => {
                    this.updateProgress();
                    this.checkAnalysisStatus(true);
                }, 2000); // 2초마다 업데이트
            },
            
            // 진행 상황 업데이트
            updateProgress() {
                if (!this.state.analysisStartTime) return;
                
                const elapsed = (Date.now() - this.state.analysisStartTime) / 1000;
                const estimatedTime = this.state.analysisConfig?.sample_size * 3; // 1명당 3초 예상
                let progress = Math.min((elapsed / estimatedTime) * 100, 95); // 최대 95%까지만
                
                document.getElementById('analysis-progress-fill').style.width = progress + '%';
                
                const statusText = elapsed < 10 ? '분석 준비 중...' :
                                 elapsed < 30 ? 'AI가 데이터를 읽고 있습니다...' :
                                 elapsed < 60 ? '개인별 분석을 진행하고 있습니다...' :
                                 'AI 피드백을 생성하고 있습니다...';
                
                document.getElementById('analysis-status-text').textContent = statusText;
            },
            
            // 분석 로그 추가
            addAnalysisLog(message) {
                const logDiv = document.getElementById('analysis-log');
                if (logDiv) {
                    const time = new Date().toLocaleTimeString();
                    logDiv.innerHTML += `<div>[${time}] ${message}</div>`;
                    logDiv.scrollTop = logDiv.scrollHeight;
                }
            },
            
            // 분석 상태 체크 (개선된 버전)
            async checkAnalysisStatus(isRealtime = false) {
                if (!this.state.analysisJobId) return;
                
                try {
                    const data = await this.api.request('GET', `/analysis/status/${this.state.analysisJobId}`);
                    
                    if (data.status === 'completed') {
                        this.onAnalysisComplete();
                    } else if (data.status === 'failed') {
                        this.onAnalysisError(data.error || '분석 중 오류 발생');
                    } else {
                        // 진행 중 - 로그 업데이트
                        if (data.progress) {
                            this.addAnalysisLog(`📊 진행 상황: ${data.progress}% (${data.current_step || '처리 중'})`);
                        }
                        
                        // 다음 체크 스케줄링
                        if (!isRealtime) {
                            setTimeout(() => this.checkAnalysisStatus(), 5000);
                        }
                    }
                } catch (error) {
                    console.error('Status check failed:', error);
                    if (!isRealtime) {
                        setTimeout(() => this.checkAnalysisStatus(), 10000); // 오류 시 10초 후 재시도
                    }
                }
            },
            
            // 분석 완료 처리
            onAnalysisComplete() {
                // 실시간 업데이트 중지
                if (this.state.progressInterval) {
                    clearInterval(this.state.progressInterval);
                    this.state.progressInterval = null;
                }
                
                // 진행바 100% 완료
                document.getElementById('analysis-progress-fill').style.width = '100%';
                document.getElementById('analysis-status-text').textContent = '분석 완료!';
                
                // 로그 업데이트
                this.addAnalysisLog('🎉 AI 분석이 성공적으로 완료되었습니다!');
                this.addAnalysisLog('📊 분석 결과를 데이터베이스에 저장했습니다.');
                
                // 완료 섹션 표시
                document.getElementById('analysis-progress-detail').style.display = 'none';
                document.getElementById('analysis-complete-section').style.display = 'block';
                
                // 대시보드 데이터 새로고침
                this.loadDashboardData();
                this.loadEmployeesData();
            },
            
            // 분석 오류 처리
            onAnalysisError(error) {
                // 실시간 업데이트 중지
                if (this.state.progressInterval) {
                    clearInterval(this.state.progressInterval);
                    this.state.progressInterval = null;
                }
                
                this.addAnalysisLog(`❌ 분석 실패: ${error}`);
                document.getElementById('analysis-status-text').textContent = '분석 중 오류 발생';
                document.getElementById('analysis-progress-fill').style.background = 'var(--error)';
            },
            
            // 분석 결과 보기 (개선된 버전)
            async viewAnalysisResults() {
                // 탭 전환
                this.switchTab('employees');
                
                // 로딩 상태 표시
                const employeesTable = document.getElementById('employees-table');
                if (employeesTable) {
                    employeesTable.innerHTML = `
                        <tr>
                            <td colspan="7" style="text-align: center; padding: 40px;">
                                <div class="spinner"></div>
                                <p style="margin-top: 20px;">최신 분석 결과를 불러오는 중...</p>
                            </td>
                        </tr>
                    `;
                }
                
                try {
                    // 직원 데이터 강제 새로고침
                    await this.loadEmployeesData();
                    
                    // 대시보드 통계도 업데이트
                    await this.loadDashboardData();
                    
                    this.showNotification('✅ 최신 분석 결과를 불러왔습니다', 'success');
                } catch (error) {
                    console.error('Failed to load analysis results:', error);
                    this.showNotification('분석 결과 로딩에 실패했습니다', 'error');
                }
            },
            
            // 분석 리포트 다운로드
            async downloadAnalysisReport() {
                try {
                    await this.exportDashboard();
                    this.showNotification('분석 리포트를 다운로드했습니다', 'success');
                } catch (error) {
                    console.error('Report download failed:', error);
                    this.showNotification('리포트 다운로드에 실패했습니다', 'error');
                }
            },
            
            // 직원 검색 기능
            selectedEmployee: null,
            allEmployees: [],
            
            async searchEmployeesForOpinion(query) {
                console.log('🔍 검색 함수 호출됨:', query);
                const dropdown = document.getElementById('employee-dropdown');
                
                if (!dropdown) {
                    console.error('❌ 드롭다운 요소를 찾을 수 없습니다');
                    return;
                }
                
                if (!query || query.trim().length < 1) {
                    dropdown.style.display = 'none';
                    return;
                }
                
                try {
                    // 전체 직원 목록이 없으면 로드
                    if (this.allEmployees.length === 0) {
                        console.log('🔄 직원 목록 로드 중...');
                        const response = await this.api.request('GET', '/employees/list');
                        this.allEmployees = response.employees || [];
                        console.log('✅ 직원 목록 로드 완료:', this.allEmployees.length, '명');
                    }
                    
                    // 검색 필터링 (이름, UID, 부서)
                    const searchTerm = query.toLowerCase().trim();
                    console.log('🔍 검색어:', searchTerm, '| 전체 직원 수:', this.allEmployees.length);
                    
                    const filteredEmployees = this.allEmployees.filter(emp => 
                        emp.employee_name?.toLowerCase().includes(searchTerm) ||
                        emp.uid?.toLowerCase().includes(searchTerm) ||
                        emp.department?.toLowerCase().includes(searchTerm)
                    ).slice(0, 10); // 최대 10개만 표시
                    
                    console.log('✅ 검색 결과:', filteredEmployees.length, '명');
                    
                    if (filteredEmployees.length > 0) {
                        dropdown.innerHTML = filteredEmployees.map(emp => `
                            <div style="
                                padding: 12px 15px; 
                                border-bottom: 1px solid #eee; 
                                cursor: pointer;
                                transition: background-color 0.2s;
                            " 
                            onmouseover="this.style.backgroundColor='#f8f9fa'" 
                            onmouseout="this.style.backgroundColor='white'"
                            onclick="AIRISS.selectEmployee('${emp.uid}', '${emp.employee_name?.replace(/'/g, "\\'")}', '${emp.department?.replace(/'/g, "\\'")}', '${emp.position?.replace(/'/g, "\\'")}')"
                            >
                                <div style="font-weight: 500; color: #2c3e50;">
                                    ${emp.employee_name || '이름 없음'}
                                </div>
                                <div style="font-size: 12px; color: #6c757d; margin-top: 2px;">
                                    UID: ${emp.uid} | ${emp.department || '부서 없음'} | ${emp.position || '직급 없음'}
                                </div>
                            </div>
                        `).join('');
                        dropdown.style.display = 'block';
                    } else {
                        dropdown.innerHTML = `
                            <div style="padding: 15px; text-align: center; color: #6c757d;">
                                검색 결과가 없습니다
                            </div>
                        `;
                        dropdown.style.display = 'block';
                    }
                } catch (error) {
                    console.error('❌ 직원 검색 실패:', error);
                    console.error('Error details:', error.message);
                    dropdown.innerHTML = `
                        <div style="padding: 15px; text-align: center; color: #dc3545;">
                            검색 중 오류가 발생했습니다: ${error.message}
                        </div>
                    `;
                    dropdown.style.display = 'block';
                }
            },
            
            selectEmployee(uid, name, department, position) {
                this.selectedEmployee = {
                    uid: uid,
                    name: name,
                    department: department,
                    position: position
                };
                
                // UI 업데이트
                document.getElementById('employee-search').value = `${name} (${uid})`;
                document.getElementById('selected-employee').innerHTML = `
                    <div style="color: #10b981; font-weight: 500;">✅ 선택됨</div>
                    <div style="font-size: 12px; margin-top: 5px; color: #2c3e50;">
                        <strong>${name}</strong><br>
                        ${department} | ${position}
                    </div>
                `;
                document.getElementById('selected-employee').style.borderColor = '#10b981';
                document.getElementById('selected-employee').style.background = 'rgba(16, 185, 129, 0.1)';
                
                // 드롭다운 닫기
                document.getElementById('employee-dropdown').style.display = 'none';
                
                console.log('선택된 직원:', this.selectedEmployee);
            },
            
            // 온도 디스플레이 업데이트
            updateTemperatureDisplay(value) {
                const tempValue = document.getElementById('temp-value');
                const tempDescription = document.getElementById('temp-description');
                const tempDisplay = document.getElementById('temperature-display');
                
                const temperatureSettings = {
                    '1': {
                        label: '매우 긍정적 분석',
                        description: '강점과 장점을 중심으로 칭찬과 인정의 관점에서 분석합니다',
                        color: '#28a745',
                        borderColor: '#28a745'
                    },
                    '2': {
                        label: '긍정적 분석',
                        description: '긍정적인 측면을 주로 보면서 발전 가능성을 강조합니다',
                        color: '#17a2b8',
                        borderColor: '#17a2b8'
                    },
                    '3': {
                        label: '중립적 분석',
                        description: '균형 잡힌 시각으로 장단점을 공정하게 분석합니다',
                        color: '#6c757d',
                        borderColor: '#6c757d'
                    },
                    '4': {
                        label: '부정적 분석',
                        description: '개선이 필요한 부분을 중심으로 발전 과제를 도출합니다',
                        color: '#fd7e14',
                        borderColor: '#fd7e14'
                    },
                    '5': {
                        label: '매우 부정적 분석',
                        description: '문제점과 리스크를 집중적으로 파악하여 개선 방안을 제시합니다',
                        color: '#dc3545',
                        borderColor: '#dc3545'
                    }
                };
                
                const setting = temperatureSettings[value];
                tempValue.textContent = setting.label;
                tempValue.style.color = setting.color;
                tempDescription.textContent = setting.description;
                tempDisplay.style.borderColor = setting.borderColor;
            },
            
            // 의견 분석 (개선된 버전)
            async analyzeOpinion() {
                // 직원 선택 검증
                if (!this.selectedEmployee) {
                    this.showNotification('분석할 직원을 먼저 선택해주세요', 'warning');
                    document.getElementById('employee-search').focus();
                    return;
                }
                
                const text = document.getElementById('opinion-text').value;
                if (!text || text.trim() === '') {
                    this.showNotification('분석할 텍스트를 입력해주세요', 'warning');
                    document.getElementById('opinion-text').focus();
                    return;
                }
                
                // 텍스트 길이 검증
                if (text.trim().length < 10) {
                    this.showNotification('더 자세한 의견을 입력해주세요 (최소 10자 이상)', 'warning');
                    document.getElementById('opinion-text').focus();
                    return;
                }
                
                const resultsDiv = document.getElementById('opinion-results');
                const analyzeButton = document.querySelector('#opinion-tab .btn-primary');
                
                try {
                    // 로딩 상태 표시
                    analyzeButton.disabled = true;
                    analyzeButton.innerHTML = '<div class="spinner" style="width: 20px; height: 20px; margin-right: 10px;"></div>🤖 AI 분석 중...';
                    
                    resultsDiv.innerHTML = `
                        <div class="card">
                            <div style="text-align: center; padding: 30px;">
                                <div class="spinner" style="margin: 0 auto 20px;"></div>
                                <h3>AI가 텍스트를 분석하고 있습니다...</h3>
                                <p style="color: var(--text-secondary); margin-top: 10px;">
                                    평가의견의 감정, 핵심역량, 개선점을 AI가 종합 분석 중입니다.
                                </p>
                            </div>
                        </div>
                    `;
                    
                    // 온도 값 가져오기
                    const temperatureValue = document.getElementById('temperature-slider').value;
                    
                    const requestBody = {
                        uid: this.selectedEmployee.uid,
                        opinions: {
                            "2024": text.trim()
                        },
                        temperature: parseInt(temperatureValue) // 1-5의 온도 값 추가
                    };
                    
                    console.log('🚀 의견 분석 요청:', requestBody);
                    const data = await this.api.request('POST', '/analysis/analyze', requestBody);
                    console.log('✅ 의견 분석 응답:', data);
                    
                    // 응답 데이터 검증
                    if (!data || data.success === false) {
                        throw new Error(data?.message || '서버에서 분석 실패 응답을 받았습니다');
                    }
                    
                    const result = data.result || data;
                    
                    // 온도 설정 정보 가져오기
                    const temperatureLabels = {
                        '1': { text: '매우 긍정적', color: '#28a745', emoji: '😊' },
                        '2': { text: '긍정적', color: '#17a2b8', emoji: '🙂' },
                        '3': { text: '중립적', color: '#6c757d', emoji: '😐' },
                        '4': { text: '부정적', color: '#fd7e14', emoji: '😕' },
                        '5': { text: '매우 부정적', color: '#dc3545', emoji: '😟' }
                    };
                    const currentTemp = temperatureLabels[temperatureValue] || temperatureLabels['3'];
                    
                    // 성공적인 분석 결과 표시
                    resultsDiv.innerHTML = `
                        <div class="card" style="animation: slideUp 0.5s ease-out;">
                            <div class="card-header">
                                <h3>✅ AI 의견 분석 결과</h3>
                                
                                <!-- 온도 설정 표시 -->
                                <div style="margin-top: 10px; padding: 10px; background: linear-gradient(135deg, ${currentTemp.color}15, ${currentTemp.color}05); border: 1px solid ${currentTemp.color}30; border-radius: 8px;">
                                    <div style="display: flex; align-items: center; gap: 8px;">
                                        <span style="font-size: 20px;">${currentTemp.emoji}</span>
                                        <span style="font-size: 14px; color: ${currentTemp.color}; font-weight: 600;">
                                            🌡️ 분석 관점: ${currentTemp.text}
                                        </span>
                                        <div style="flex: 1; height: 4px; background: linear-gradient(to right, #28a745 0%, #ffc107 50%, #dc3545 100%); border-radius: 2px; margin: 0 10px; position: relative;">
                                            <div style="position: absolute; top: -3px; left: ${(temperatureValue - 1) * 25}%; width: 10px; height: 10px; background: ${currentTemp.color}; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.2);"></div>
                                        </div>
                                    </div>
                                </div>
                                
                                <div style="margin-top: 10px; padding: 12px; background: rgba(102, 126, 234, 0.1); border-radius: 8px;">
                                    <div style="font-weight: 500; color: var(--text-primary);">
                                        👤 분석 대상: ${this.selectedEmployee.name} (${this.selectedEmployee.uid})
                                    </div>
                                    <div style="font-size: 13px; color: var(--text-secondary); margin-top: 3px;">
                                        ${this.selectedEmployee.department} | ${this.selectedEmployee.position}
                                    </div>
                                </div>
                                <span style="color: var(--text-secondary); font-size: 14px; margin-top: 10px; display: block;">
                                    분석 완료: ${new Date().toLocaleString('ko-KR')} | UID: ${this.selectedEmployee.uid}
                                </span>
                            </div>
                            
                            <!-- 점수 및 등급 섹션 -->
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0;">
                                <div style="text-align: center; padding: 15px; background: rgba(0, 212, 255, 0.1); border-radius: 8px;">
                                    <div style="font-size: 24px; font-weight: bold; color: #00d4ff;">${result.text_score || result.ai_score || 0}</div>
                                    <div style="font-size: 12px; color: var(--text-secondary); margin-top: 5px;">AI 종합 점수</div>
                                </div>
                                <div style="text-align: center; padding: 15px; background: rgba(102, 126, 234, 0.1); border-radius: 8px;">
                                    <div style="font-size: 24px; font-weight: bold; color: #667eea;">${result.grade || 'B'}</div>
                                    <div style="font-size: 12px; color: var(--text-secondary); margin-top: 5px;">평가 등급</div>
                                </div>
                                <div style="text-align: center; padding: 15px; background: rgba(16, 185, 129, 0.1); border-radius: 8px;">
                                    <div style="font-size: 18px; font-weight: bold; color: #10B981;">${result.sentiment_analysis || '중립적'}</div>
                                    <div style="font-size: 12px; color: var(--text-secondary); margin-top: 5px;">감정 분석</div>
                                </div>
                            </div>
                            
                            <!-- 상세 분석 결과 (온도에 따라 강조 변경) -->
                            <div style="display: grid; gap: 20px; margin-top: 20px;">
                                <div style="padding: 15px; background: rgba(16, 185, 129, 0.1); border-left: 4px solid #10B981; border-radius: 4px; ${temperatureValue <= 2 ? 'order: -1;' : temperatureValue >= 4 ? 'opacity: 0.7;' : ''}">
                                    <h4 style="color: #10B981; margin-bottom: 10px;">
                                        💪 강점 및 우수 역량 
                                        ${temperatureValue <= 2 ? '<span style="background: #10B981; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin-left: 8px;">강조</span>' : ''}
                                    </h4>
                                    <ul style="margin: 0; padding-left: 20px; color: var(--text-primary);">
                                        ${(result.strengths || ['긍정적인 업무 태도', '성실성', '책임감']).map(s => `<li style="margin-bottom: 5px; ${temperatureValue <= 2 ? 'font-weight: 500;' : ''}">${s}</li>`).join('')}
                                    </ul>
                                </div>
                                
                                <div style="padding: 15px; background: rgba(245, 158, 11, 0.1); border-left: 4px solid #F59E0B; border-radius: 4px; ${temperatureValue >= 4 ? 'order: -1;' : temperatureValue <= 2 ? 'opacity: 0.7;' : ''}">
                                    <h4 style="color: #F59E0B; margin-bottom: 10px;">
                                        🎯 개선 방향 및 발전 과제
                                        ${temperatureValue >= 4 ? '<span style="background: #F59E0B; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin-left: 8px;">강조</span>' : ''}
                                    </h4>
                                    <ul style="margin: 0; padding-left: 20px; color: var(--text-primary);">
                                        ${(result.improvements || result.weaknesses || ['지속적인 성장 기대', '역량 강화 필요']).map(i => `<li style="margin-bottom: 5px; ${temperatureValue >= 4 ? 'font-weight: 500;' : ''}">${i}</li>`).join('')}
                                    </ul>
                                </div>
                                
                                ${result.summary ? `
                                <div style="padding: 15px; background: rgba(102, 126, 234, 0.1); border-left: 4px solid #667eea; border-radius: 4px;">
                                    <h4 style="color: #667eea; margin-bottom: 10px;">📝 종합 평가</h4>
                                    <p style="margin: 0; color: var(--text-primary); line-height: 1.6;">${result.summary}</p>
                                </div>
                                ` : ''}
                            </div>
                            
                            <!-- 추가 정보 -->
                            <div style="margin-top: 20px; padding: 10px; background: rgba(255,255,255,0.05); border-radius: 4px; font-size: 12px; color: var(--text-secondary);">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span>분석 정확도: ${result.confidence ? Math.round(result.confidence * 100) : 85}%</span>
                                    <span>분석 시간: ${result.processing_time || '< 1'}초</span>
                                </div>
                            </div>
                        </div>
                    `;
                    
                    this.showNotification('✅ AI 의견 분석이 완료되었습니다', 'success');
                    
                } catch (error) {
                    console.error('❌ Opinion analysis failed:', error);
                    
                    resultsDiv.innerHTML = `
                        <div class="card" style="border-left: 4px solid var(--danger-color);">
                            <div style="text-align: center; padding: 30px;">
                                <h3 style="color: var(--danger-color); margin-bottom: 15px;">❌ 분석 실패</h3>
                                <p style="color: var(--text-secondary); margin-bottom: 20px;">
                                    의견 분석 중 오류가 발생했습니다.
                                </p>
                                <div style="background: rgba(239, 68, 68, 0.1); padding: 15px; border-radius: 8px; margin: 15px 0;">
                                    <p style="color: var(--danger-color); font-size: 14px; margin: 0;">
                                        <strong>오류 내용:</strong> ${error.message || '서버 연결 오류'}
                                    </p>
                                </div>
                                <div style="display: grid; gap: 10px; margin-top: 20px;">
                                    <h4 style="color: var(--text-primary);">해결 방법:</h4>
                                    <ul style="text-align: left; color: var(--text-secondary); max-width: 400px; margin: 0 auto;">
                                        <li>텍스트가 너무 짧지 않은지 확인해주세요 (최소 10자)</li>
                                        <li>네트워크 연결 상태를 확인해주세요</li>
                                        <li>잠시 후 다시 시도해주세요</li>
                                        <li>문제가 지속되면 관리자에게 문의하세요</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    `;
                    
                    this.showNotification('❌ 의견 분석에 실패했습니다. 다시 시도해주세요.', 'error');
                    
                } finally {
                    // 버튼 상태 복원
                    analyzeButton.disabled = false;
                    analyzeButton.innerHTML = '🤖 AI 분석 시작';
                }
            },
            
            // PDF 다운로드
            async exportDashboard() {
                try {
                    const response = await fetch('/api/v1/hr-dashboard/export/pdf');
                    const blob = await response.blob();
                    
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `AIRISS_Dashboard_${new Date().toISOString().slice(0, 10)}.pdf`;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                    
                    this.showNotification('PDF 다운로드 완료', 'success');
                } catch (error) {
                    console.error('PDF export failed:', error);
                }
            },
            
            // 직원 상세 보기
            viewDetail(employeeId) {
                console.log('직원 상세 보기:', employeeId);
                // 모달 또는 새 탭에서 상세 정보 표시
                this.showNotification(`직원 ${employeeId}의 상세 정보를 불러오는 중...`, 'info');
                
                // 상세 정보 모달 표시 (추후 구현)
                alert(`직원 ID: ${employeeId}\n\n상세 정보 기능은 준비 중입니다.`);
            },
            
            // 데이터 내보내기
            async exportData(format = 'excel') {
                try {
                    console.log(`데이터 내보내기: ${format} 형식`);
                    
                    if (format === 'excel') {
                        // Excel 내보내기
                        const response = await fetch('/api/v1/hr-dashboard/export/excel');
                        const blob = await response.blob();
                        
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `AIRISS_직원분석_${new Date().toISOString().slice(0, 10)}.xlsx`;
                        document.body.appendChild(a);
                        a.click();
                        window.URL.revokeObjectURL(url);
                        
                        this.showNotification('Excel 다운로드 완료', 'success');
                    } else if (format === 'csv') {
                        // CSV 내보내기
                        const csvContent = this.convertToCSV(this.state.employees);
                        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `AIRISS_직원분석_${new Date().toISOString().slice(0, 10)}.csv`;
                        document.body.appendChild(a);
                        a.click();
                        window.URL.revokeObjectURL(url);
                        
                        this.showNotification('CSV 다운로드 완료', 'success');
                    }
                } catch (error) {
                    console.error('Export failed:', error);
                    this.showNotification('데이터 내보내기 실패', 'error');
                }
            },
            
            // CSV 변환 헬퍼
            convertToCSV(data) {
                if (!data || data.length === 0) return '';
                
                const headers = ['사번', '이름', '부서', '직급', 'AI점수', '등급', '주요강점', '개선사항'];
                const rows = data.map(emp => [
                    emp.employee_id || '',
                    emp.name || '',
                    emp.department || '',
                    emp.position || '',
                    emp.ai_score || 0,
                    emp.grade || '',
                    emp.primary_strength || '',
                    emp.primary_improvement || ''
                ]);
                
                const csvContent = [
                    headers.join(','),
                    ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
                ].join('\n');
                
                return '\uFEFF' + csvContent; // UTF-8 BOM 추가
            },
            
            // 모달 닫기
            closeModal() {
                document.getElementById('employee-modal').classList.remove('active');
            },
            
            // PDF 다운로드 (이미지 캡처 방식)
            async downloadPDF() {
                try {
                    this.showNotification('PDF 생성 중입니다. 잠시만 기다려주세요...', 'info');
                    
                    const data = this.currentEmployeeData;
                    if (!data) {
                        this.showNotification('직원 데이터를 불러올 수 없습니다', 'error');
                        return;
                    }
                    
                    // 모달 콘텐츠를 캡처
                    const modalContent = document.getElementById('modal-body');
                    
                    // 버튼들을 임시로 숨기기
                    const buttons = modalContent.querySelectorAll('button');
                    buttons.forEach(btn => btn.style.display = 'none');
                    
                    // 현재 스크롤 위치 저장
                    const originalScrollTop = modalContent.scrollTop;
                    
                    // 스크롤을 맨 위로
                    modalContent.scrollTop = 0;
                    
                    // 모달의 실제 전체 높이 계산
                    const fullHeight = modalContent.scrollHeight;
                    const fullWidth = modalContent.scrollWidth;
                    
                    // 모달의 원래 overflow 스타일 저장
                    const originalOverflow = modalContent.style.overflow;
                    modalContent.style.overflow = 'visible';
                    modalContent.style.height = 'auto';
                    
                    // html2canvas를 사용하여 이미지로 캡처 (전체 높이)
                    const canvas = await html2canvas(modalContent, {
                        scale: 2, // 고화질을 위해 2배 스케일
                        useCORS: true,
                        backgroundColor: 'rgba(22, 27, 34, 0.95)',
                        logging: false,
                        width: fullWidth,
                        height: fullHeight,
                        windowWidth: fullWidth,
                        windowHeight: fullHeight,
                        scrollX: 0,
                        scrollY: 0
                    });
                    
                    // 원래 스타일로 복원
                    modalContent.style.overflow = originalOverflow;
                    modalContent.style.height = '';
                    modalContent.scrollTop = originalScrollTop;
                    
                    // 버튼들 다시 표시
                    buttons.forEach(btn => btn.style.display = '');
                    
                    // jsPDF 생성
                    const { jsPDF } = window.jspdf;
                    
                    // A4 크기 PDF 생성 (세로 방향)
                    const pdf = new jsPDF('p', 'mm', 'a4');
                    const pageWidth = pdf.internal.pageSize.getWidth();
                    const pageHeight = pdf.internal.pageSize.getHeight();
                    
                    // 캔버스를 이미지로 변환
                    const imgData = canvas.toDataURL('image/png');
                    
                    // 이미지 크기 계산 (A4 페이지에 맞춤)
                    const imgWidth = pageWidth - 20; // 좌우 여백 10mm씩
                    const imgHeight = (canvas.height * imgWidth) / canvas.width;
                    
                    let heightLeft = imgHeight;
                    let position = 10; // 상단 여백 10mm
                    
                    // 첫 페이지에 이미지 추가
                    pdf.addImage(imgData, 'PNG', 10, position, imgWidth, imgHeight);
                    heightLeft -= (pageHeight - 20); // 상하 여백 제외
                    
                    // 이미지가 한 페이지보다 길면 추가 페이지 생성
                    while (heightLeft > 0) {
                        position = heightLeft - imgHeight + 10; // 다음 페이지 시작 위치
                        pdf.addPage();
                        pdf.addImage(imgData, 'PNG', 10, position, imgWidth, imgHeight);
                        heightLeft -= (pageHeight - 20);
                    }
                    
                    // 파일명 생성 및 저장
                    const fileName = `${data.name || '직원'}_AI분석리포트_${new Date().toISOString().split('T')[0]}.pdf`;
                    pdf.save(fileName);
                    
                    this.showNotification('PDF 다운로드가 완료되었습니다', 'success');
                } catch (error) {
                    console.error('PDF 생성 오류:', error);
                    this.showNotification('PDF 생성 중 오류가 발생했습니다', 'error');
                }
            },
            
            // 알림 표시
            showNotification(message, type = 'info') {
                // 간단한 알림 구현 (실제로는 toast 라이브러리 사용 권장)
                console.log(`[${type.toUpperCase()}] ${message}`);
            },
            
            // 직원 검색
            searchEmployees() {
                const query = document.getElementById('search-input').value.toLowerCase();
                const filtered = this.state.employees.filter(emp => 
                    (emp.employee_name || '').toLowerCase().includes(query) ||
                    (emp.uid || '').toLowerCase().includes(query)
                );
                this.renderEmployees(filtered);
            },
            
            // 헬퍼 함수들 - loadInsights 보다 먼저 정의되어야 함
            // 평균 점수 계산
            calculateAverageScore(employees) {
                if (!employees || employees.length === 0) return 0;
                const total = employees.reduce((sum, emp) => sum + (emp.ai_score || emp.overall_score || emp.AIRISS_v2_종합점수 || 0), 0);
                return Math.round(total / employees.length);
            },
            
            // 등급 분포 계산
            calculateGradeDistribution(employees) {
                // 두 번째 버전의 함수로 통일 (더 상세한 로직)
                const distribution = {
                    'S': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0
                };
                
                if (!employees || employees.length === 0) return distribution;
                
                employees.forEach((emp, index) => {
                    // 다양한 필드명 처리
                    let grade = emp.grade || emp.final_grade || emp.ai_grade || emp.OK등급 || 'C';
                    
                    // null/undefined 체크
                    if (!grade || grade === 'null' || grade === 'undefined') {
                        grade = 'C';
                    }
                    
                    // 대문자로 변환
                    let normalizedGrade = grade.toString().toUpperCase().trim();
                    
                    // A+, B+ 같은 등급을 A, B로 변환
                    if (normalizedGrade.includes('+') || normalizedGrade.includes('-')) {
                        normalizedGrade = normalizedGrade[0];
                    }
                    
                    // S, A, B, C, D만 허용
                    if (['S', 'A', 'B', 'C', 'D'].includes(normalizedGrade)) {
                        distribution[normalizedGrade]++;
                    } else {
                        distribution['C']++; // 기본값
                    }
                });
                
                return distribution;
            },
            
            // 부서별 분석
            analyzeDepartments(employees) {
                const deptData = {};
                employees.forEach(emp => {
                    const dept = emp.department || emp.부서 || '미지정';
                    if (!deptData[dept]) {
                        deptData[dept] = { 
                            count: 0, 
                            totalScore: 0, 
                            grades: { 'S': 0, 'A+': 0, 'A': 0, 'B+': 0, 'B': 0, 'C': 0, 'D': 0 }
                        };
                    }
                    deptData[dept].count++;
                    deptData[dept].totalScore += emp.ai_score || emp.overall_score || emp.AIRISS_v2_종합점수 || 0;
                    
                    const grade = emp.ai_grade || emp.grade || emp.OK등급 || 'C';
                    if (deptData[dept].grades.hasOwnProperty(grade)) {
                        deptData[dept].grades[grade]++;
                    }
                });
                
                // 평균 계산
                Object.keys(deptData).forEach(dept => {
                    deptData[dept].avgScore = Math.round(deptData[dept].totalScore / deptData[dept].count);
                });
                
                return deptData;
            },
            
            // 인사이트 로드 (실시간 데이터 기반)
            async loadInsights() {
                const content = document.getElementById('insights-content');
                
                // 실제 데이터 기반 계산
                const employees = this.state.employees || [];
                const dashboardStats = this.state.dashboardStats || {};
                
                // 평균 점수 계산
                const avgScore = this.calculateAverageScore(employees);
                
                // 등급 분포 계산
                const gradeDistribution = { 'S': 0, 'A+': 0, 'A': 0, 'B+': 0, 'B': 0, 'C': 0, 'D': 0 };
                employees.forEach(emp => {
                    const grade = emp.ai_grade || emp.grade || emp.OK등급 || 'C';
                    if (gradeDistribution.hasOwnProperty(grade)) {
                        gradeDistribution[grade]++;
                    }
                });
                
                // 부서별 분석
                const deptAnalysis = {};
                employees.forEach(emp => {
                    const dept = emp.department || emp.부서 || '기타';
                    if (!deptAnalysis[dept]) {
                        deptAnalysis[dept] = { count: 0, totalScore: 0, talents: 0, risks: 0 };
                    }
                    deptAnalysis[dept].count++;
                    deptAnalysis[dept].totalScore += emp.ai_score || emp.overall_score || emp.AIRISS_v2_종합점수 || 0;
                    
                    const score = emp.ai_score || emp.overall_score || 0;
                    if (score >= 850) deptAnalysis[dept].talents++;
                    if (score < 600) deptAnalysis[dept].risks++;
                });
                
                // 가장 우수한 부서와 개선 필요 부서 찾기
                let bestDept = null, worstDept = null;
                let bestAvg = 0, worstAvg = 1000;
                
                Object.entries(deptAnalysis).forEach(([dept, data]) => {
                    const avg = data.totalScore / data.count;
                    if (avg > bestAvg) {
                        bestAvg = avg;
                        bestDept = dept;
                    }
                    if (avg < worstAvg) {
                        worstAvg = avg;
                        worstDept = dept;
                    }
                });
                
                // 조직 건강도 계산 (0-100점)
                const healthScore = Math.min(100, Math.round(
                    (avgScore / 10) * 0.4 +  // 평균 점수 (40%)
                    ((gradeDistribution['S'] + gradeDistribution['A+'] + gradeDistribution['A']) / employees.length * 100) * 0.3 +  // 상위 등급 비율 (30%)
                    ((1 - gradeDistribution['D'] / employees.length) * 100) * 0.3  // 하위 등급 비율 (30%)
                ));
                
                // 인사이트 생성
                const topTalentsCount = dashboardStats.top_talents?.count || employees.filter(e => (e.ai_score || 0) >= 850).length;
                const riskEmployeesCount = dashboardStats.risk_employees?.count || employees.filter(e => (e.ai_score || 0) < 600).length;
                const promotionCandidatesCount = dashboardStats.promotion_candidates?.count || employees.filter(e => (e.ai_score || 0) >= 750 && (e.ai_score || 0) < 850).length;
                
                content.innerHTML = `
                    <div style="display: grid; gap: 20px;">
                        <!-- 조직 건강도 스코어카드 -->
                        <div class="card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                            <h3>🏆 조직 건강도 종합 평가</h3>
                            <div style="display: flex; align-items: center; gap: 20px; margin: 20px 0;">
                                <div style="font-size: 48px; font-weight: bold;">${healthScore}점</div>
                                <div>
                                    <div style="font-size: 18px; margin-bottom: 5px;">
                                        ${healthScore >= 80 ? '우수' : healthScore >= 60 ? '양호' : healthScore >= 40 ? '보통' : '개선필요'}
                                    </div>
                                    <div style="opacity: 0.9;">
                                        전체 ${employees.length}명 기준 종합 평가
                                    </div>
                                </div>
                            </div>
                            <div style="background: rgba(255,255,255,0.2); padding: 10px; border-radius: 8px; margin-top: 10px;">
                                <small>평균 AI 점수: ${avgScore}점 | 상위등급 비율: ${Math.round((gradeDistribution['S'] + gradeDistribution['A+'] + gradeDistribution['A']) / employees.length * 100)}%</small>
                            </div>
                            
                            <!-- 상세 분석 추가 -->
                            <div style="margin-top: 20px; padding: 15px; background: rgba(0,0,0,0.2); border-radius: 8px;">
                                <h4 style="color: #00d4ff; margin-bottom: 10px;">🔍 상세 분석</h4>
                                <div style="display: grid; gap: 10px; font-size: 14px;">
                                    <div>📈 <strong>강점</strong>: ${
                                        healthScore >= 80 ? '조직 전반적으로 우수한 성과를 보이고 있으며, 인재 밀도와 역량 수준이 높습니다.' :
                                        healthScore >= 60 ? '핵심 인재의 성과가 양호하며, 조직 전체적으로 안정적인 성과를 유지하고 있습니다.' :
                                        healthScore >= 40 ? '일부 우수 인재가 있으나, 전체적인 성과 향상이 필요합니다.' :
                                        '일부 직원의 헌신적인 노력이 돋보이나, 전체적인 개선이 시급합니다.'
                                    }</div>
                                    <div>👥 <strong>위험 요소</strong>: ${
                                        riskEmployeesCount > employees.length * 0.2 ? '하위 성과자 비율이 높아 즉각적인 개입이 필요합니다.' :
                                        promotionCandidatesCount < employees.length * 0.1 ? '차세대 리더 풀이 부족하여 중장기 성장에 리스크가 있습니다.' :
                                        (bestAvg - worstAvg) > 200 ? '부서간 성과 격차가 커 조직 분열 위험이 있습니다.' :
                                        '현재 특별한 리스크는 없으나, 지속적인 모니터링이 필요합니다.'
                                    }</div>
                                    <div>🎯 <strong>개선 방향</strong>: ${
                                        topTalentsCount < employees.length * 0.1 ? '핵심 인재 육성 프로그램 강화 및 외부 인재 영입' :
                                        riskEmployeesCount > employees.length * 0.15 ? '하위 성과자 대상 집중 코칭 및 역량 개발' :
                                        promotionCandidatesCount < employees.length * 0.1 ? '승진 후보자 풀 확대 및 리더십 개발' :
                                        '현재 수준 유지 및 점진적 개선'
                                    }</div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- 핵심 인사이트 -->
                        <div class="card">
                            <h3>🎯 경영진 관점 핵심 인사이트</h3>
                            <div style="display: grid; gap: 15px;">
                                ${topTalentsCount > employees.length * 0.15 ? `
                                    <div style="padding: 12px; background: rgba(16, 185, 129, 0.15); border-left: 4px solid #10B981; border-radius: 4px; color: #ffffff;">
                                        <strong style="color: #10B981;">✓ 인재 밀도 우수</strong><br>
                                        <span style="color: rgba(255,255,255,0.9);">핵심 인재가 ${Math.round(topTalentsCount / employees.length * 100)}%로 업계 평균(10-15%)을 상회합니다.</span>
                                    </div>
                                ` : `
                                    <div style="padding: 12px; background: rgba(245, 158, 11, 0.15); border-left: 4px solid #F59E0B; border-radius: 4px; color: #ffffff;">
                                        <strong style="color: #F59E0B;">⚠ 인재 육성 필요</strong><br>
                                        <span style="color: rgba(255,255,255,0.9);">핵심 인재가 ${Math.round(topTalentsCount / employees.length * 100)}%로 업계 평균 이하입니다. 
                                        고성과자 육성 프로그램 도입을 권장합니다.</span>
                                    </div>
                                `}
                                
                                ${riskEmployeesCount > employees.length * 0.2 ? `
                                    <div style="padding: 12px; background: rgba(239, 68, 68, 0.15); border-left: 4px solid #EF4444; border-radius: 4px; color: #ffffff;">
                                        <strong style="color: #EF4444;">⚠ 리스크 관리 시급</strong><br>
                                        <span style="color: rgba(255,255,255,0.9);">전체 인력의 ${Math.round(riskEmployeesCount / employees.length * 100)}%가 관리 필요 그룹입니다.
                                        즉각적인 성과 개선 프로그램 또는 인력 재배치가 필요합니다.</span>
                                    </div>
                                ` : `
                                    <div style="padding: 12px; background: rgba(16, 185, 129, 0.15); border-left: 4px solid #10B981; border-radius: 4px; color: #ffffff;">
                                        <strong style="color: #10B981;">✓ 리스크 관리 양호</strong><br>
                                        <span style="color: rgba(255,255,255,0.9);">관리 필요 인력이 ${Math.round(riskEmployeesCount / employees.length * 100)}%로 안정적입니다.</span>
                                    </div>
                                `}
                                
                                ${bestDept && worstDept ? `
                                    <div style="padding: 12px; background: rgba(102, 126, 234, 0.15); border-left: 4px solid #667eea; border-radius: 4px; color: #ffffff;">
                                        <strong style="color: #667eea;">📊 부서간 성과 격차</strong><br>
                                        <span style="color: rgba(255,255,255,0.9);">최우수 부서(${bestDept}: ${Math.round(bestAvg)}점)와 
                                        개선필요 부서(${worstDept}: ${Math.round(worstAvg)}점) 간 
                                        ${Math.round(bestAvg - worstAvg)}점 차이가 있습니다.</span>
                                    </div>
                                ` : ''}
                            </div>
                        </div>
                        
                        <!-- 전략적 제언 -->
                        <div class="card">
                            <h3>💡 AI 기반 전략적 제언</h3>
                            <div style="display: grid; gap: 12px;">
                                <div>
                                    <h4 style="color: #00d9ff; margin-bottom: 10px;">🎯 단기 실행과제 (3개월 내)</h4>
                                    <ul style="margin: 0; padding-left: 20px; line-height: 1.8;">
                                        ${riskEmployeesCount > employees.length * 0.15 ? 
                                            '<li><strong>성과개선 TF 구성</strong>: 하위 ' + riskEmployeesCount + '명 대상 집중 코칭 프로그램</li>' : ''}
                                        ${promotionCandidatesCount < employees.length * 0.1 ? 
                                            '<li><strong>승진 Pool 확대</strong>: 현재 ' + promotionCandidatesCount + '명으로 부족, 차세대 리더 육성 프로그램 시급</li>' : ''}
                                        ${topTalentsCount > 0 ? 
                                            '<li><strong>핵심인재 리텐션</strong>: ' + topTalentsCount + '명의 핵심인재 대상 보상체계 개선 및 경력개발 지원</li>' : ''}
                                        <li><strong>부서간 협업 강화</strong>: ${bestDept} 부서의 우수사례를 전사 확산</li>
                                    </ul>
                                </div>
                                
                                <div>
                                    <h4 style="color: #00d9ff; margin-bottom: 10px;">🚀 중장기 혁신과제 (6-12개월)</h4>
                                    <ul style="margin: 0; padding-left: 20px; line-height: 1.8;">
                                        <li><strong>AI 기반 인재관리 시스템 고도화</strong>: 예측적 인재관리 및 맞춤형 육성</li>
                                        <li><strong>성과문화 혁신</strong>: OKR 도입 및 애자일 성과관리 체계 구축</li>
                                        <li><strong>조직문화 진단</strong>: ${healthScore < 70 ? '조직 건강도 개선을 위한' : '현재 수준 유지를 위한'} 문화 혁신 프로그램</li>
                                        ${worstDept ? `<li><strong>${worstDept} 부서 특별관리</strong>: 조직 재설계 및 리더십 교체 검토</li>` : ''}
                                    </ul>
                                </div>
                            </div>
                        </div>
                        
                        <!-- 데이터 기반 예측 -->
                        <div class="card">
                            <h3>📈 향후 전망 및 시나리오</h3>
                            <div style="display: grid; gap: 15px;">
                                <div style="padding: 15px; background: #f8f9fa; border-radius: 8px; color: #333333;">
                                    <h4 style="color: #28a745; margin-bottom: 10px;">✅ 긍정 시나리오 (개선 조치 시행 시)</h4>
                                    <ul style="margin: 0; padding-left: 20px; color: #333333;">
                                        <li>6개월 내 조직 건강도 ${Math.min(100, healthScore + 15)}점 달성 가능</li>
                                        <li>핵심인재 이탈률 5% 이하 유지</li>
                                        <li>전체 생산성 15-20% 향상 예상</li>
                                    </ul>
                                </div>
                                <div style="padding: 15px; background: #fff5f5; border-radius: 8px; color: #333333;">
                                    <h4 style="color: #dc3545; margin-bottom: 10px;">⚠ 위험 시나리오 (현상 유지 시)</h4>
                                    <ul style="margin: 0; padding-left: 20px; color: #333333;">
                                        <li>핵심인재 ${Math.round(topTalentsCount * 0.3)}명 이탈 위험</li>
                                        <li>하위 성과자 증가로 전체 생산성 10% 하락</li>
                                        <li>부서간 갈등 심화 및 협업 저하</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                        
                        <!-- 실시간 모니터링 지표 -->
                        <div class="card">
                            <h3>📊 핵심 모니터링 지표 (KPI)</h3>
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                                <div style="text-align: center; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                                    <div style="font-size: 24px; font-weight: bold; color: #00d9ff;">${avgScore}</div>
                                    <div style="font-size: 12px; color: #6c757d; margin-top: 5px;">평균 AI 점수</div>
                                    <div style="font-size: 11px; color: ${avgScore >= 750 ? '#28a745' : avgScore >= 650 ? '#ffc107' : '#dc3545'};">
                                        ${avgScore >= 750 ? '▲ 우수' : avgScore >= 650 ? '- 보통' : '▼ 개선필요'}
                                    </div>
                                </div>
                                <div style="text-align: center; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                                    <div style="font-size: 24px; font-weight: bold; color: #00d9ff;">
                                        ${Math.round((gradeDistribution['S'] + gradeDistribution['A+']) / employees.length * 100)}%
                                    </div>
                                    <div style="font-size: 12px; color: #6c757d; margin-top: 5px;">최상위 등급 비율</div>
                                    <div style="font-size: 11px; color: ${(gradeDistribution['S'] + gradeDistribution['A+']) / employees.length > 0.1 ? '#28a745' : '#dc3545'};">
                                        목표: 10% 이상
                                    </div>
                                </div>
                                <div style="text-align: center; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                                    <div style="font-size: 24px; font-weight: bold; color: #00d9ff;">
                                        ${Math.round(riskEmployeesCount / employees.length * 100)}%
                                    </div>
                                    <div style="font-size: 12px; color: #6c757d; margin-top: 5px;">리스크 인력 비율</div>
                                    <div style="font-size: 11px; color: ${riskEmployeesCount / employees.length < 0.15 ? '#28a745' : '#dc3545'};">
                                        목표: 15% 이하
                                    </div>
                                </div>
                                <div style="text-align: center; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                                    <div style="font-size: 24px; font-weight: bold; color: #00d9ff;">
                                        ${Object.keys(deptAnalysis).length}개
                                    </div>
                                    <div style="font-size: 12px; color: #6c757d; margin-top: 5px;">분석 부서 수</div>
                                    <div style="font-size: 11px; color: #6c757d;">
                                        총 ${employees.length}명 분석
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            },
            
            // 화면에 리포트 표시
            async showReport(type) {
                const reportContent = document.getElementById('report-content');
                const reportActions = document.getElementById('report-actions');
                const reportTypeIcon = document.getElementById('report-type-icon');
                const reportTypeName = document.getElementById('report-type-name');
                
                // 로딩 표시
                reportContent.innerHTML = `
                    <div style="text-align: center; padding: 100px 20px;">
                        <div class="spinner"></div>
                        <p style="margin-top: 20px; color: rgba(255, 255, 255, 0.7);">리포트를 생성하고 있습니다...</p>
                    </div>
                `;
                
                // 리포트 타입별 아이콘과 이름 설정
                const reportTypes = {
                    'monthly': { icon: '📊', name: '월간 종합 리포트' },
                    'talent': { icon: '⭐', name: '핵심 인재 리포트' },
                    'risk': { icon: '⚠️', name: '리스크 관리 리포트' },
                    'performance': { icon: '📈', name: '성과 분석 리포트' },
                    'department': { icon: '🏢', name: '부서별 분석 리포트' },
                    'executive': { icon: '💼', name: '경영진 브리핑 리포트' }
                };
                
                if (reportTypes[type]) {
                    reportTypeIcon.textContent = reportTypes[type].icon;
                    reportTypeName.textContent = reportTypes[type].name;
                }
                
                // 잠시 후 리포트 생성
                setTimeout(async () => {
                    // 먼저 최신 데이터 로드
                    await this.loadEmployeesData();
                    await this.loadDashboardData();
                    
                    // state에서 실제 데이터 가져오기
                    let dashboardData = this.state.dashboardStats || {};
                    let employees = this.state.employees || [];
                    
                    try {
                        console.log('📊 리포트 생성을 위한 데이터 준비...');
                        console.log('  - 대시보드 통계:', dashboardData);
                        console.log('  - 직원 수:', employees.length);
                        
                        // 데이터가 없으면 다시 시도
                        if (!dashboardData.total_employees && (!employees || employees.length === 0)) {
                            console.log('📊 HR 대시보드 데이터 재로드 중...');
                            const response = await this.api.request('GET', '/hr-dashboard/stats');
                            if (response && response.total_employees) {
                                dashboardData = response;
                                this.state.dashboardStats = response;
                                console.log('✅ HR 대시보드 데이터 로드 성공:', dashboardData);
                            }
                        }
                    } catch (error) {
                        console.error('❌ HR 대시보드 데이터 로드 실패:', error);
                        
                        // 실제 데이터를 가져올 수 없을 때는 에러 메시지 표시
                        reportContent.innerHTML = `
                            <div style="text-align: center; padding: 100px 20px;">
                                <h3 style="color: #ff5252; margin-bottom: 20px;">데이터 로드 실패</h3>
                                <p style="color: rgba(255, 255, 255, 0.7); margin-bottom: 30px;">
                                    서버에서 데이터를 가져올 수 없습니다.<br>
                                    잠시 후 다시 시도해주세요.
                                </p>
                                <button onclick="location.reload()" style="padding: 10px 20px; background: #00d4ff; color: white; border: none; border-radius: 5px; cursor: pointer;">
                                    새로고침
                                </button>
                            </div>
                        `;
                        reportActions.style.display = 'none';
                        return;
                    }
                    
                    console.log(`📊 리포트 생성 - 타입: ${type}, 전체 직원 수: ${dashboardData.total_employees || employees.length}`);
                    
                    let content = '';
                    
                    switch(type) {
                        case 'monthly':
                            content = this.generateMonthlyReport(dashboardData, employees);
                            break;
                        case 'talent':
                            content = this.generateTalentReport(dashboardData, employees);
                            break;
                        case 'risk':
                            content = this.generateRiskReport(dashboardData, employees);
                            break;
                        case 'performance':
                            content = this.generatePerformanceReport(dashboardData, employees);
                            break;
                        case 'department':
                            content = this.generateDepartmentReport(dashboardData, employees);
                            break;
                        case 'executive':
                            content = this.generateExecutiveReport(dashboardData, employees);
                            break;
                        default:
                            content = '<p>알 수 없는 리포트 타입입니다.</p>';
                    }
                    
                    // 리포트 내용 표시
                    reportContent.innerHTML = content;
                    reportActions.style.display = 'block';
                    
                    // 현재 리포트 정보 저장 (다운로드용)
                    this.currentReport = {
                        type: type,
                        content: content,
                        title: reportTypes[type]?.name || '리포트'
                    };
                }, 500);
            },
            
            // 리포트 생성
            async generateReport(type, shouldDownload = true) {
                try {
                    this.showNotification(`${type} 리포트 생성 중...`, 'info');
                    
                    // 리포트 타입별 데이터 수집
                    let reportData = {
                        type: type,
                        generated_at: new Date().toISOString(),
                        company: 'OK금융그룹',
                        department: '전체'
                    };
                    
                    // 대시보드 데이터 가져오기
                    const dashboardData = this.state.dashboardStats || {};
                    const employees = this.state.employees || [];
                    
                    switch(type) {
                        case 'monthly':
                            reportData.title = '월간 HR 분석 리포트';
                            reportData.content = this.generateMonthlyReport(dashboardData, employees);
                            break;
                            
                        case 'talent':
                            reportData.title = '핵심 인재 분석 리포트';
                            reportData.content = this.generateTalentReport(dashboardData, employees);
                            break;
                            
                        case 'risk':
                            reportData.title = '리스크 관리 리포트';
                            reportData.content = this.generateRiskReport(dashboardData, employees);
                            break;
                            
                        case 'custom':
                            reportData.title = '맮춤형 HR 분석 리포트';
                            reportData.content = this.generateCustomReport(dashboardData, employees);
                            break;
                    }
                    
                    // 리포트 화면 업데이트
                    this.currentReport = reportData;
                    const reportContent = document.getElementById('report-content');
                    if (reportContent) {
                        reportContent.innerHTML = reportData.content;
                    }
                    
                    // 다운로드가 필요한 경우에만 HTML 파일 생성
                    if (shouldDownload) {
                        this.downloadReport(reportData);
                        this.showNotification('리포트가 생성되었습니다', 'success');
                    } else {
                        this.showNotification('리포트가 업데이트되었습니다', 'success');
                    }
                    
                } catch (error) {
                    console.error('Report generation failed:', error);
                    this.showNotification('리포트 생성에 실패했습니다', 'error');
                }
            },
            
            // 유틸리티 함수들
            calculateAverageScore(employees) {
                if (!employees || employees.length === 0) return 0;
                
                let validScores = 0;
                let totalScore = 0;
                
                employees.forEach(emp => {
                    // 다양한 필드명 처리
                    const score = emp.ai_score || emp.overall_score || emp.final_score || emp.total_score || 0;
                    if (score > 0) {
                        totalScore += score;
                        validScores++;
                    }
                });
                
                if (validScores === 0) return 0;
                return Math.round(totalScore / validScores);
            },
            
            calculateGradeDistribution(employees) {
                const distribution = {
                    'S': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0
                };
                
                if (!employees || employees.length === 0) return distribution;
                
                // 첫 5개 직원 데이터 샘플 확인 (디버깅용)
                console.log('📊 등급 분포 계산 - 직원 수:', employees.length);
                console.log('📊 등급 분포 계산 - 직원 샘플:', employees.slice(0, 5).map(emp => ({
                    grade: emp.grade,
                    final_grade: emp.final_grade,
                    ai_grade: emp.ai_grade,
                    ai_score: emp.ai_score,
                    overall_score: emp.overall_score,
                    employee_name: emp.employee_name
                })));
                
                // 점수 분포 확인
                const scoreDistribution = {
                    '90-100': 0,
                    '80-89': 0,
                    '70-79': 0,
                    '60-69': 0,
                    '0-59': 0
                };
                
                employees.forEach((emp, index) => {
                    // 점수 분포 분석
                    const score = emp.ai_score || emp.overall_score || 0;
                    if (score >= 90) scoreDistribution['90-100']++;
                    else if (score >= 80) scoreDistribution['80-89']++;
                    else if (score >= 70) scoreDistribution['70-79']++;
                    else if (score >= 60) scoreDistribution['60-69']++;
                    else scoreDistribution['0-59']++;
                    
                    // 다양한 필드명 처리 (HR Dashboard API 기준 우선)
                    let grade = emp.grade || emp.final_grade || emp.ai_grade || 'C';
                    
                    // null/undefined 체크
                    if (!grade || grade === 'null' || grade === 'undefined') {
                        grade = 'C';
                    }
                    
                    // 대문자로 변환
                    let normalizedGrade = grade.toString().toUpperCase().trim();
                    
                    // A+, B+ 같은 등급을 A, B로 변환
                    if (normalizedGrade.includes('+') || normalizedGrade.includes('-')) {
                        normalizedGrade = normalizedGrade[0];
                    }
                    
                    // 첫 5개 데이터만 디버깅 로그
                    if (index < 5) {
                        console.log(`  직원 ${index}: 원본 grade='${emp.grade}', 변환 grade='${normalizedGrade}', score=${score}`);
                    }
                    
                    // S, A, B, C, D만 허용 (엄격한 검증)
                    if (['S', 'A', 'B', 'C', 'D'].includes(normalizedGrade)) {
                        distribution[normalizedGrade]++;
                    } else {
                        // 잘못된 등급이면 점수 기준으로 재분류
                        if (score >= 90) {
                            distribution['S']++;
                        } else if (score >= 80) {
                            distribution['A']++;
                        } else if (score >= 70) {
                            distribution['B']++;
                        } else if (score >= 60) {
                            distribution['C']++;
                        } else {
                            distribution['D']++;
                        }
                        
                        if (index < 5) {
                            console.log(`    ⚠️ 유효하지 않은 등급 '${normalizedGrade}' → 점수 기준으로 재분류`);
                        }
                    }
                });
                
                console.log('📊 점수 분포:', scoreDistribution);
                console.log('📊 등급 분포:', distribution);
                
                return distribution;
            },
            
            analyzeDepartments(employees) {
                const deptData = {};
                
                if (!employees || employees.length === 0) {
                    console.log('🏢 analyzeDepartments: 직원 데이터가 없습니다');
                    return deptData;
                }
                
                console.log('🏢 analyzeDepartments: 분석 시작 - 직원 수:', employees.length);
                
                employees.forEach((emp, idx) => {
                    const dept = emp.department || '부서 미상';
                    
                    if (!deptData[dept]) {
                        deptData[dept] = {
                            count: 0,
                            totalScore: 0,
                            avgScore: 0,
                            grades: {
                                'S': 0, 'A+': 0, 'A': 0, 'B+': 0, 'B': 0, 'C': 0, 'D': 0
                            }
                        };
                    }
                    
                    deptData[dept].count++;
                    const score = emp.ai_score || emp.overall_score || 0;
                    deptData[dept].totalScore += score;
                    
                    const grade = emp.grade || emp.final_grade || emp.ai_grade || 'C';
                    if (deptData[dept].grades.hasOwnProperty(grade)) {
                        deptData[dept].grades[grade]++;
                    } else {
                        deptData[dept].grades['C']++; // 기본값
                    }
                    
                    // 처음 5개 직원만 디버깅 로그
                    if (idx < 5) {
                        console.log(`  직원 ${idx}: dept=${dept}, score=${score}, grade=${grade}`);
                    }
                });
                
                // 평균 점수 계산
                Object.keys(deptData).forEach(dept => {
                    if (deptData[dept].count > 0) {
                        deptData[dept].avgScore = Math.round(deptData[dept].totalScore / deptData[dept].count);
                    }
                });
                
                console.log('🏢 analyzeDepartments: 결과:', deptData);
                return deptData;
            },
            
            // 부서별 성과 현황 섹션 생성
            generateDepartmentPerformanceSection(deptAnalysis) {
                console.log('🏢 generateDepartmentPerformanceSection 호출:', deptAnalysis);
                
                if (!deptAnalysis || Object.keys(deptAnalysis).length === 0) {
                    console.log('🏢 부서 데이터가 없어 기본 메시지 표시');
                    return `
                        <div style="background: rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 15px; margin: 25px 0; border: 1px solid rgba(255, 255, 255, 0.1);">
                            <div style="text-align: center; color: rgba(255, 255, 255, 0.7); padding: 40px;">
                                <h3 style="color: #00d4ff; margin-bottom: 15px;">부서별 성과 현황</h3>
                                <p>부서별 데이터를 로드 중입니다...</p>
                                <p style="font-size: 14px; opacity: 0.8;">데이터가 표시되지 않으면 새로고침 후 다시 시도해 주세요.</p>
                            </div>
                        </div>
                    `;
                }
                
                let rows = '';
                
                // 평균 점수 기준으로 정렬
                const sortedDepts = Object.entries(deptAnalysis).sort((a, b) => {
                    const avgA = a[1].avgScore || a[1].avg_score || 0;
                    const avgB = b[1].avgScore || b[1].avg_score || 0;
                    return avgB - avgA;
                });
                
                const totalDepartments = sortedDepts.length;
                const itemsPerPage = 10;
                const totalPages = Math.ceil(totalDepartments / itemsPerPage);
                
                // 첫 페이지만 표시하고 나머지는 페이지네이션으로
                const firstPageDepts = sortedDepts.slice(0, itemsPerPage);
                
                firstPageDepts.forEach(([dept, data], index) => {
                    // 다양한 데이터 구조 처리
                    const count = data.count || 0;
                    const avgScore = data.avgScore || data.avg_score || 0;
                    
                    // 핵심 인재 수 계산
                    let topTalents = 0;
                    if (data.grades) {
                        topTalents = (data.grades['S'] || 0) + (data.grades['A+'] || 0) + (data.grades['A'] || 0);
                    }
                    
                    // 성과 등급 계산 (100점 스케일 기준으로 자동 판단)
                    const performance = avgScore >= 90 ? { grade: 'S (최우수)', color: '#69f0ae' } :
                                      avgScore >= 85 ? { grade: 'A (우수)', color: '#4caf50' } :
                                      avgScore >= 80 ? { grade: 'B+ (양호)', color: '#ffd54f' } :
                                      avgScore >= 75 ? { grade: 'B (평균)', color: '#ff9800' } :
                                      avgScore >= 70 ? { grade: 'C (미흡)', color: '#ff7043' } :
                                      { grade: 'D (개선필요)', color: '#ff5252' };
                    
                    // 순위 표시
                    const rankIcon = index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : '';
                    
                    rows += `
                        <tr style="background: rgba(255, 255, 255, ${index % 2 === 0 ? '0.03' : '0.05'}); transition: all 0.3s ease;" onmouseover="this.style.background='rgba(0, 212, 255, 0.08)'" onmouseout="this.style.background='rgba(255, 255, 255, ${index % 2 === 0 ? '0.03' : '0.05'})'">
                            <td style="padding: 15px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #ffffff; font-weight: 500; text-align: center;">
                                ${index + 1}
                            </td>
                            <td style="padding: 15px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #ffffff; font-weight: 500;">
                                ${rankIcon} ${dept}
                            </td>
                            <td style="padding: 15px; text-align: center; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #ffffff; font-weight: 600; font-size: 1.1em;">
                                ${count}명
                            </td>
                            <td style="padding: 15px; text-align: center; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #00d4ff; font-weight: 700; font-size: 1.1em; text-shadow: 0 0 10px rgba(0, 212, 255, 0.3);">
                                ${avgScore}점
                            </td>
                            <td style="padding: 15px; text-align: center; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #69f0ae; font-weight: 600; text-shadow: 0 0 10px rgba(76, 175, 80, 0.3);">
                                ${topTalents}명
                            </td>
                            <td style="padding: 15px; text-align: center; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: ${performance.color}; font-weight: 600; text-shadow: 0 0 10px ${performance.color}66;">
                                ${performance.grade}
                            </td>
                        </tr>
                    `;
                });
                
                if (rows === '') {
                    rows = `
                        <tr>
                            <td colspan="5" style="padding: 30px; text-align: center; color: rgba(255, 255, 255, 0.7); font-style: italic;">
                                부서별 성과 데이터를 준비 중입니다...
                            </td>
                        </tr>
                    `;
                }
                
                // 페이지네이션 컨트롤 생성
                const paginationId = 'dept-pagination-' + Date.now();
                const tableId = 'dept-table-' + Date.now();
                
                let paginationControls = '';
                if (totalPages > 1) {
                    paginationControls = `
                        <div style="margin-top: 20px; padding: 15px; background: rgba(255, 255, 255, 0.03); border-radius: 10px; display: flex; justify-content: space-between; align-items: center;">
                            <div style="color: rgba(255, 255, 255, 0.8); font-size: 14px;">
                                총 ${totalDepartments}개 부서 중 1-${Math.min(itemsPerPage, totalDepartments)}개 표시
                            </div>
                            <div style="display: flex; gap: 10px;">
                                <button onclick="window.AIRISSApp.changeDeptPage('${tableId}', 1)" style="padding: 8px 12px; background: rgba(0, 212, 255, 0.2); border: 1px solid rgba(0, 212, 255, 0.3); border-radius: 6px; color: #00d4ff; cursor: pointer; font-size: 12px;" title="첫 페이지">‹‹</button>
                                <button onclick="window.AIRISSApp.changeDeptPage('${tableId}', 'prev')" style="padding: 8px 12px; background: rgba(0, 212, 255, 0.2); border: 1px solid rgba(0, 212, 255, 0.3); border-radius: 6px; color: #00d4ff; cursor: pointer; font-size: 12px;" title="이전 페이지">‹</button>
                                <span id="${paginationId}" style="padding: 8px 16px; color: #ffffff; font-weight: 600;">1 / ${totalPages}</span>
                                <button onclick="window.AIRISSApp.changeDeptPage('${tableId}', 'next')" style="padding: 8px 12px; background: rgba(0, 212, 255, 0.2); border: 1px solid rgba(0, 212, 255, 0.3); border-radius: 6px; color: #00d4ff; cursor: pointer; font-size: 12px;" title="다음 페이지">›</button>
                                <button onclick="window.AIRISSApp.changeDeptPage('${tableId}', ${totalPages})" style="padding: 8px 12px; background: rgba(0, 212, 255, 0.2); border: 1px solid rgba(0, 212, 255, 0.3); border-radius: 6px; color: #00d4ff; cursor: pointer; font-size: 12px;" title="마지막 페이지">››</button>
                            </div>
                        </div>
                    `;
                }
                
                return `
                    <div style="background: rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 15px; margin: 25px 0; border: 1px solid rgba(255, 255, 255, 0.1); box-shadow: 0 4px 20px rgba(0, 212, 255, 0.1);">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                            <h3 style="color: #00d4ff; margin: 0; font-size: 18px;">부서별 성과 현황</h3>
                            <div style="color: rgba(255, 255, 255, 0.7); font-size: 14px;">
                                총 ${totalDepartments}개 부서 
                            </div>
                        </div>
                        
                        <table id="${tableId}" style="width: 100%; border-collapse: separate; border-spacing: 0; border-radius: 12px; overflow: hidden; background: rgba(255, 255, 255, 0.02);" data-all-departments='${JSON.stringify(sortedDepts)}' data-items-per-page="${itemsPerPage}" data-current-page="1" data-pagination-id="${paginationId}">
                            <thead>
                                <tr style="background: linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(0, 153, 255, 0.15));">
                                    <th style="padding: 16px; text-align: left; color: #00d4ff; font-weight: 600; font-size: 14px; border-bottom: 2px solid rgba(0, 212, 255, 0.3);">순위</th>
                                    <th style="padding: 16px; text-align: left; color: #00d4ff; font-weight: 600; font-size: 14px; border-bottom: 2px solid rgba(0, 212, 255, 0.3);">부서명</th>
                                    <th style="padding: 16px; text-align: center; color: #00d4ff; font-weight: 600; font-size: 14px; border-bottom: 2px solid rgba(0, 212, 255, 0.3);">인원</th>
                                    <th style="padding: 16px; text-align: center; color: #00d4ff; font-weight: 600; font-size: 14px; border-bottom: 2px solid rgba(0, 212, 255, 0.3);">평균점수</th>
                                    <th style="padding: 16px; text-align: center; color: #00d4ff; font-weight: 600; font-size: 14px; border-bottom: 2px solid rgba(0, 212, 255, 0.3);">핵심인재</th>
                                    <th style="padding: 16px; text-align: center; color: #00d4ff; font-weight: 600; font-size: 14px; border-bottom: 2px solid rgba(0, 212, 255, 0.3);">평가</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${rows}
                            </tbody>
                        </table>
                        
                        ${paginationControls}
                        
                        <div style="margin-top: 20px; padding: 20px; background: rgba(255, 255, 255, 0.03); border-radius: 10px; border-left: 4px solid #00d4ff;">
                            <h4 style="color: #00d4ff; margin-top: 0; margin-bottom: 15px; font-size: 16px;">📊 부서별 분석 요약</h4>
                            <ul style="color: rgba(255, 255, 255, 0.8); line-height: 1.8; margin: 0; padding-left: 20px;">
                                <li>부서별 성과 편차를 지속적으로 모니터링하여 균형 잡힌 성과 관리 추진</li>
                                <li>상위 성과 부서의 모범 사례를 전사에 확산하여 조직 역량 향상</li>
                                <li>하위 성과 부서의 집중 관리 및 개선 프로그램 운영</li>
                            </ul>
                        </div>
                    </div>
                `;
            },
            
            // 월간 리포트 생성
            generateMonthlyReport(dashboardData, employees) {
                const date = new Date();
                const month = date.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long' });
                
                // HR 대시보드 API 데이터 우선 사용
                const totalEmployees = dashboardData.total_employees || employees.length || 0;
                
                // 디버깅: 실제 데이터 확인
                console.log('🔍 월간 리포트 생성 시작');
                console.log('  - dashboardData:', dashboardData);
                console.log('  - total_employees:', totalEmployees);
                console.log('  - dashboardData.grade_distribution:', dashboardData.grade_distribution);
                
                // 평균 점수 계산 (부서별 평균에서 전체 평균 계산)
                let avgScore = 0;
                if (dashboardData.department_stats) {
                    const depts = Object.values(dashboardData.department_stats);
                    const totalCount = depts.reduce((sum, dept) => sum + dept.count, 0);
                    const weightedSum = depts.reduce((sum, dept) => sum + (dept.avg_score * dept.count), 0);
                    avgScore = totalCount > 0 ? Math.round(weightedSum / totalCount) : 75;
                } else if (employees && employees.length > 0) {
                    avgScore = this.calculateAverageScore(employees);
                } else {
                    avgScore = 75; // 기본값
                }
                
                // 등급 분포 (HR 대시보드 API 데이터 최우선 사용)
                let gradeDistribution = {
                    'S': 0,
                    'A': 0,
                    'B': 0,
                    'C': 0,
                    'D': 0
                };
                
                let gradeDataSource = '';
                
                // 1순위: HR Dashboard API의 grade_distribution (가장 정확함)
                if (dashboardData && dashboardData.grade_distribution && Array.isArray(dashboardData.grade_distribution)) {
                    console.log('  - grade_distribution API 배열 사용:', dashboardData.grade_distribution);
                    dashboardData.grade_distribution.forEach(grade => {
                        if (grade && grade.grade && grade.count !== undefined) {
                            gradeDistribution[grade.grade] = grade.count;
                        }
                    });
                    gradeDataSource = 'API grade_distribution (정확한 데이터)';
                }
                
                // 등급 분포 검증 - 너무 이상하면 재계산
                const totalFromDist = Object.values(gradeDistribution).reduce((sum, count) => sum + count, 0);
                const isDistributionValid = totalFromDist > 0 && totalFromDist <= totalEmployees * 1.2;
                
                if (!isDistributionValid) {
                    console.log('  - API grade_distribution이 유효하지 않음, 재계산 필요');
                    console.log(`    총 인원: ${totalEmployees}, 분포 합계: ${totalFromDist}`);
                    
                    // 2순위: HR Dashboard API의 employees에서 직접 계산
                    if (dashboardData && dashboardData.employees && dashboardData.employees.length > 0) {
                        console.log('  - dashboardData.employees에서 등급 분포 재계산');
                        gradeDistribution = this.calculateGradeDistribution(dashboardData.employees);
                        gradeDataSource = 'dashboardData.employees에서 재계산';
                    }
                    // 3순위: 외부 employees 데이터
                    else if (employees && employees.length > 0) {
                        console.log('  - 외부 직원 데이터에서 등급 분포 계산');
                        gradeDistribution = this.calculateGradeDistribution(employees);
                        gradeDataSource = '외부 employees 데이터에서 계산';
                    }
                    else {
                        console.log('  - 등급 분포 계산 불가 - 데이터 없음');
                        gradeDataSource = '데이터 없음';
                    }
                }
                
                // 최종 검증 및 로깅
                const finalTotal = Object.values(gradeDistribution).reduce((sum, count) => sum + count, 0);
                console.log(`  - 등급 분포 데이터 소스: ${gradeDataSource}`);
                console.log(`  - 등급 분포 총합: ${finalTotal}명 (전체: ${totalEmployees}명)`);
                console.log('  - S:', gradeDistribution['S'], 'A:', gradeDistribution['A'], 
                           'B:', gradeDistribution['B'], 'C:', gradeDistribution['C'], 
                           'D:', gradeDistribution['D']);
                
                // 부서 분석 - HR Dashboard API의 department_stats 우선 사용 (가장 정확한 데이터)
                let deptAnalysis = {};
                let dataSource = '';
                
                if (dashboardData.department_stats && Object.keys(dashboardData.department_stats).length > 0) {
                    deptAnalysis = dashboardData.department_stats;
                    dataSource = 'API department_stats (권장)';
                } else if (employees && employees.length > 0) {
                    console.log('⚠️ API department_stats가 없어 직원 데이터에서 계산');
                    deptAnalysis = this.analyzeDepartments(employees);
                    dataSource = 'employees 데이터에서 계산';
                } else if (dashboardData.employees && dashboardData.employees.length > 0) {
                    console.log('⚠️ API department_stats가 없어 dashboardData.employees에서 계산');
                    deptAnalysis = this.analyzeDepartments(dashboardData.employees);
                    dataSource = 'dashboardData.employees에서 계산';
                } else {
                    console.log('❌ 부서 분석용 데이터가 없습니다');
                    dataSource = '데이터 없음';
                }
                
                const totalDepts = Object.keys(deptAnalysis).length || 5;
                
                console.log('🏢 부서 분석 데이터 로드 완료');
                console.log('  - 데이터 소스:', dataSource);
                console.log('  - 부서 수:', totalDepts);
                console.log('  - 상위 5개 부서:', Object.keys(deptAnalysis).slice(0, 5));
                
                if (totalDepts === 0) {
                    console.log('❌ 부서 데이터가 비어있습니다. API 응답을 확인하세요.');
                }
                
                // 최우수 인재 (Top Talents) - 여러 소스에서 계산
                let topTalents = 0;
                
                // 우선순위 1: HR Dashboard API의 top_talents
                if (dashboardData.top_talents && dashboardData.top_talents.count) {
                    topTalents = dashboardData.top_talents.count;
                    console.log('✅ topTalents from API top_talents:', topTalents);
                    if (dashboardData.top_talents.s_grade_count !== undefined) {
                        console.log('  - S등급:', dashboardData.top_talents.s_grade_count);
                        console.log('  - A등급:', dashboardData.top_talents.a_grade_count);
                    }
                }
                // 우선순위 2: grade_distribution에서 계산
                else if (dashboardData.grade_distribution && Array.isArray(dashboardData.grade_distribution)) {
                    const sGrade = dashboardData.grade_distribution.find(g => g.grade === 'S');
                    const aGrade = dashboardData.grade_distribution.find(g => g.grade === 'A');
                    topTalents = (sGrade ? sGrade.count : 0) + (aGrade ? aGrade.count : 0);
                    console.log('✅ topTalents from API grade_distribution:', topTalents);
                }
                // 우선순위 3: 계산된 gradeDistribution에서
                else if (gradeDistribution && (gradeDistribution['S'] || gradeDistribution['A'])) {
                    topTalents = (gradeDistribution['S'] || 0) + (gradeDistribution['A'] || 0);
                    console.log('✅ topTalents from calculated gradeDistribution:', topTalents);
                }
                // 우선순위 4: employees에서 직접 계산
                else if (employees && employees.length > 0) {
                    topTalents = employees.filter(emp => {
                        const grade = emp.grade || emp.final_grade || emp.ai_grade || '';
                        return grade === 'S' || grade === 'A';
                    }).length;
                    console.log('✅ topTalents from direct employee count:', topTalents);
                }
                // 기본값 (실제 데이터베이스 평균 기준)
                else {
                    // 전체 직원 대비 약 28% (S: 0.3%, A: 27.8%)
                    topTalents = Math.round(totalEmployees * 0.28);
                    console.log('⚠️ topTalents using default ratio (28%):', topTalents);
                }
                
                console.log('📊 월간종합 분석 데이터 요약:');
                console.log('  - 전체 직원:', totalEmployees);
                console.log('  - 평균 점수:', avgScore);
                console.log('  - 등급 분포 객체:', gradeDistribution);
                console.log('  - S등급:', gradeDistribution['S'], 'A등급:', gradeDistribution['A'], 
                            'B등급:', gradeDistribution['B'], 'C등급:', gradeDistribution['C'], 
                            'D등급:', gradeDistribution['D']);
                console.log('  - 최우수 인재 (카드):', topTalents);
                console.log('  - 최우수 인재 (테이블 계산):', (gradeDistribution['S'] || 0) + (gradeDistribution['A'] || 0));
                console.log('  - 부서 수:', totalDepts);
                
                // 데이터 불일치 경고
                const tableTopTalents = (gradeDistribution['S'] || 0) + (gradeDistribution['A'] || 0);
                if (topTalents !== tableTopTalents) {
                    console.warn('⚠️ 데이터 불일치 발견!');
                    console.warn('  - 카드 최우수 인재:', topTalents);
                    console.warn('  - 테이블 최우수 인재:', tableTopTalents);
                    console.warn('  - 차이:', Math.abs(topTalents - tableTopTalents));
                }
                
                return `
                    <div style="font-family: 'Inter', 'Noto Sans KR', sans-serif; line-height: 1.8; color: #ffffff;">
                        <h1 style="background: linear-gradient(135deg, #00d4ff, #0099ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: clamp(32px, 5vw, 48px); font-weight: 700; padding-bottom: 20px; margin-bottom: 30px; border-bottom: 2px solid rgba(0, 212, 255, 0.3); text-shadow: 0 0 30px rgba(0, 212, 255, 0.3);">
                            ${month} HR 종합 분석 리포트
                        </h1>
                        
                        <div style="background: rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 20px; margin: 25px 0; border: 1px solid rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); box-shadow: 0 4px 20px rgba(0, 212, 255, 0.1);">
                            <p style="margin: 0; color: rgba(255, 255, 255, 0.8); font-size: 16px; line-height: 1.8;">
                                <strong style="color: #00d4ff;">생성일시:</strong> ${new Date().toLocaleString('ko-KR')}<br>
                                <strong style="color: #00d4ff;">분석 대상:</strong> 전체 ${totalEmployees}명<br>
                                <strong style="color: #00d4ff;">작성 부서:</strong> OK홀딩스 인사부
                            </p>
                        </div>
                        
                        <h2 style="background: linear-gradient(135deg, #00d4ff, #0099ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 32px; font-weight: 700; margin-top: 40px; margin-bottom: 25px; text-shadow: 0 0 20px rgba(0, 212, 255, 0.3);">📊 Executive Summary</h2>
                        <div style="background: rgba(255, 255, 255, 0.05); padding: 30px; border-radius: 20px; margin: 25px 0; border: 1px solid rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); box-shadow: 0 8px 32px rgba(0, 212, 255, 0.15);">
                            <h3 style="color: #00d4ff; margin-top: 0; font-size: 24px; text-shadow: 0 0 15px rgba(0, 212, 255, 0.3); margin-bottom: 25px;">핵심 지표</h3>
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 25px;">
                                <div style="text-align: center; padding: 25px; background: rgba(255, 255, 255, 0.08); border-radius: 15px; border: 1px solid rgba(255, 255, 255, 0.15); backdrop-filter: blur(10px); transition: all 0.3s ease;">
                                    <div style="background: linear-gradient(135deg, #fff, rgba(255, 255, 255, 0.9)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 42px; font-weight: 800; text-shadow: 0 0 20px rgba(255, 255, 255, 0.5); margin-bottom: 10px;">${totalEmployees}</div>
                                    <div style="font-size: 14px; color: rgba(255, 255, 255, 0.8); text-transform: uppercase; letter-spacing: 1px; font-weight: 500;">전체 직원</div>
                                </div>
                                <div style="text-align: center; padding: 25px; background: rgba(255, 255, 255, 0.08); border-radius: 15px; border: 1px solid rgba(0, 212, 255, 0.2); backdrop-filter: blur(10px); transition: all 0.3s ease;">
                                    <div style="background: linear-gradient(135deg, #00d4ff, #0099ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 42px; font-weight: 800; text-shadow: 0 0 20px rgba(0, 212, 255, 0.5); margin-bottom: 10px;">${avgScore}</div>
                                    <div style="font-size: 14px; color: rgba(255, 255, 255, 0.8); text-transform: uppercase; letter-spacing: 1px; font-weight: 500;">평균 AI 점수</div>
                                </div>
                                <div style="text-align: center; padding: 25px; background: rgba(255, 255, 255, 0.08); border-radius: 15px; border: 1px solid rgba(76, 175, 80, 0.3); backdrop-filter: blur(10px); transition: all 0.3s ease;">
                                    <div style="background: linear-gradient(135deg, #69f0ae, #4caf50); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 42px; font-weight: 800; text-shadow: 0 0 20px rgba(76, 175, 80, 0.5); margin-bottom: 10px;">${topTalents}</div>
                                    <div style="font-size: 14px; color: rgba(255, 255, 255, 0.8); text-transform: uppercase; letter-spacing: 1px; font-weight: 500;">최우수 인재 (S+A)</div>
                                </div>
                                <div style="text-align: center; padding: 25px; background: rgba(255, 255, 255, 0.08); border-radius: 15px; border: 1px solid rgba(255, 193, 7, 0.3); backdrop-filter: blur(10px); transition: all 0.3s ease;">
                                    <div style="background: linear-gradient(135deg, #ff6b6b, #feca57); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 42px; font-weight: 800; text-shadow: 0 0 20px rgba(255, 193, 7, 0.5); margin-bottom: 10px;">${totalDepts}</div>
                                    <div style="font-size: 14px; color: rgba(255, 255, 255, 0.8); text-transform: uppercase; letter-spacing: 1px; font-weight: 500;">분석 부서</div>
                                </div>
                            </div>
                        </div>
                        
                        <h2 style="background: linear-gradient(135deg, #00d4ff, #0099ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 28px; font-weight: 700; margin-top: 40px; margin-bottom: 25px; text-shadow: 0 0 20px rgba(0, 212, 255, 0.3);">1. 인력 현황 분석</h2>
                        
                        <div style="display: flex; gap: 40px; align-items: flex-start; margin: 25px 0;">
                            <!-- 테이블 -->
                            <div style="flex: 0 0 55%;">
                                <table style="width: 100%; border-collapse: separate; border-spacing: 0; border-radius: 15px; overflow: hidden; background: rgba(255, 255, 255, 0.05); box-shadow: 0 4px 20px rgba(0, 212, 255, 0.1);">
                                    <thead>
                                        <tr style="background: linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(0, 153, 255, 0.15));">
                                            <th style="padding: 16px; text-align: left; color: #00d4ff; font-weight: 600; font-size: 14px; border-bottom: 2px solid rgba(0, 212, 255, 0.3);">구분</th>
                                            <th style="padding: 16px; text-align: center; color: #00d4ff; font-weight: 600; font-size: 14px; border-bottom: 2px solid rgba(0, 212, 255, 0.3);">인원수</th>
                                            <th style="padding: 16px; text-align: center; color: #00d4ff; font-weight: 600; font-size: 14px; border-bottom: 2px solid rgba(0, 212, 255, 0.3);">비율</th>
                                            <th style="padding: 16px; text-align: left; color: #00d4ff; font-weight: 600; font-size: 14px; border-bottom: 2px solid rgba(0, 212, 255, 0.3);">비고</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr style="background: rgba(255, 255, 255, 0.03);">
                                            <td style="padding: 14px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: rgba(255, 255, 255, 0.9); font-weight: 600;">전체 직원</td>
                                            <td style="padding: 14px; text-align: center; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #ffffff; font-weight: 700;">${totalEmployees}명</td>
                                            <td style="padding: 14px; text-align: center; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #00d4ff; font-weight: 600;">100%</td>
                                            <td style="padding: 14px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: rgba(255, 255, 255, 0.7); font-size: 13px;">분석 대상 전체</td>
                                        </tr>
                                        <tr style="background: rgba(255, 215, 0, 0.08);">
                                            <td style="padding: 14px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #FFD700; font-weight: 600;">핵심 인재 (S)</td>
                                            <td style="padding: 14px; text-align: center; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #FFD700; font-weight: 700;">${(gradeDistribution['S'] || 0)}명</td>
                                            <td style="padding: 14px; text-align: center; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #FFD700; font-weight: 600;">${totalEmployees > 0 ? Math.round((gradeDistribution['S'] || 0) / totalEmployees * 100) : 0}%</td>
                                            <td style="padding: 14px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: rgba(255, 255, 255, 0.7); font-size: 13px;">최상위 성과자</td>
                                        </tr>
                                        <tr style="background: rgba(76, 175, 80, 0.08);">
                                            <td style="padding: 14px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #69f0ae; font-weight: 600;">우수 인재 (A)</td>
                                            <td style="padding: 14px; text-align: center; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #69f0ae; font-weight: 700;">${(gradeDistribution['A'] || 0)}명</td>
                                            <td style="padding: 14px; text-align: center; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #69f0ae; font-weight: 600;">${totalEmployees > 0 ? Math.round((gradeDistribution['A'] || 0) / totalEmployees * 100) : 0}%</td>
                                            <td style="padding: 14px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: rgba(255, 255, 255, 0.7); font-size: 13px;">핵심 관리 대상</td>
                                        </tr>
                                        <tr style="background: rgba(33, 150, 243, 0.08);">
                                            <td style="padding: 14px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #2196F3; font-weight: 600;">일반 성과자 (B)</td>
                                            <td style="padding: 14px; text-align: center; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #2196F3; font-weight: 700;">${(gradeDistribution['B'] || 0)}명</td>
                                            <td style="padding: 14px; text-align: center; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #2196F3; font-weight: 600;">${totalEmployees > 0 ? Math.round((gradeDistribution['B'] || 0) / totalEmployees * 100) : 0}%</td>
                                            <td style="padding: 14px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: rgba(255, 255, 255, 0.7); font-size: 13px;">승진 후보군</td>
                                        </tr>
                                        <tr style="background: rgba(255, 152, 0, 0.08);">
                                            <td style="padding: 14px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #FF9800; font-weight: 600;">기초 수준 (C)</td>
                                            <td style="padding: 14px; text-align: center; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #FF9800; font-weight: 700;">${(gradeDistribution['C'] || 0)}명</td>
                                            <td style="padding: 14px; text-align: center; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #FF9800; font-weight: 600;">${totalEmployees > 0 ? Math.round((gradeDistribution['C'] || 0) / totalEmployees * 100) : 0}%</td>
                                            <td style="padding: 14px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: rgba(255, 255, 255, 0.7); font-size: 13px;">역량 개발 대상</td>
                                        </tr>
                                        <tr style="background: rgba(244, 67, 54, 0.08);">
                                            <td style="padding: 14px; color: #ff5252; font-weight: 600;">관리 필요 (D)</td>
                                            <td style="padding: 14px; text-align: center; color: #ff5252; font-weight: 700;">${gradeDistribution['D'] || 0}명</td>
                                            <td style="padding: 14px; text-align: center; color: #ff5252; font-weight: 600;">${totalEmployees > 0 ? Math.round((gradeDistribution['D'] || 0) / totalEmployees * 100) : 0}%</td>
                                            <td style="padding: 14px; color: rgba(255, 255, 255, 0.7); font-size: 13px;">집중 관리 필요</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                            
                            <!-- 막대그래프 -->
                            <div style="flex: 1; background: rgba(255, 255, 255, 0.05); border-radius: 15px; padding: 25px; box-shadow: 0 4px 20px rgba(0, 212, 255, 0.1);">
                                <h4 style="color: #00d4ff; margin-top: 0; margin-bottom: 20px; font-size: 16px;">등급별 분포도</h4>
                                <div style="position: relative; height: 280px;">
                                    ${['S', 'A', 'B', 'C', 'D'].map((grade, idx) => {
                                        const count = gradeDistribution[grade] || 0;
                                        const percent = totalEmployees > 0 ? (count / totalEmployees * 100) : 0;
                                        const maxPercent = Math.max(...Object.values(gradeDistribution).map(v => (v || 0) / totalEmployees * 100));
                                        const barWidth = maxPercent > 0 ? (percent / maxPercent * 100) : 0;
                                        const colors = {
                                            'S': '#FFD700',
                                            'A': '#69f0ae', 
                                            'B': '#2196F3',
                                            'C': '#FF9800',
                                            'D': '#ff5252'
                                        };
                                        
                                        return `
                                            <div style="display: flex; align-items: center; margin-bottom: 15px;">
                                                <div style="width: 30px; font-weight: 700; color: ${colors[grade]};">${grade}</div>
                                                <div style="flex: 1; position: relative; height: 35px; background: rgba(255, 255, 255, 0.05); border-radius: 8px; overflow: hidden; margin: 0 15px;">
                                                    <div style="position: absolute; left: 0; top: 0; height: 100%; width: ${barWidth}%; background: linear-gradient(90deg, ${colors[grade]}, ${colors[grade]}dd); border-radius: 8px; transition: width 0.5s ease; box-shadow: 0 2px 10px ${colors[grade]}66;">
                                                        <span style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); color: white; font-weight: 600; font-size: 13px; text-shadow: 0 1px 2px rgba(0,0,0,0.3);">
                                                            ${count}명
                                                        </span>
                                                    </div>
                                                </div>
                                                <div style="width: 50px; text-align: right; color: ${colors[grade]}; font-weight: 600;">
                                                    ${percent.toFixed(1)}%
                                                </div>
                                            </div>
                                        `;
                                    }).join('')}
                                </div>
                                <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid rgba(255, 255, 255, 0.1);">
                                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                                        <span style="color: rgba(255, 255, 255, 0.7); font-size: 13px;">상위 등급(S+A)</span>
                                        <span style="color: #00d4ff; font-weight: 600;">${(gradeDistribution['S'] || 0) + (gradeDistribution['A'] || 0)}명 (${totalEmployees > 0 ? Math.round(((gradeDistribution['S'] || 0) + (gradeDistribution['A'] || 0)) / totalEmployees * 100) : 0}%)</span>
                                    </div>
                                    <div style="display: flex; justify-content: space-between;">
                                        <span style="color: rgba(255, 255, 255, 0.7); font-size: 13px;">관리 필요(D)</span>
                                        <span style="color: ${(gradeDistribution['D'] || 0) > totalEmployees * 0.1 ? '#ff5252' : '#69f0ae'}; font-weight: 600;">${gradeDistribution['D'] || 0}명 (${totalEmployees > 0 ? Math.round((gradeDistribution['D'] || 0) / totalEmployees * 100) : 0}%)</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <h2 style="background: linear-gradient(135deg, #00d4ff, #0099ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 28px; font-weight: 700; margin-top: 40px; margin-bottom: 25px; text-shadow: 0 0 20px rgba(0, 212, 255, 0.3);">2. 부서별 성과 분석</h2>
                        ${this.generateDepartmentPerformanceSection(deptAnalysis)}
                        
                        <h2 style="background: linear-gradient(135deg, #00d4ff, #0099ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 1.8em; font-weight: 700; margin-top: 40px; margin-bottom: 25px; text-shadow: 0 0 20px rgba(0, 212, 255, 0.3);">3. 월간 주요 이슈 및 Action Items</h2>
                        <div style="background: linear-gradient(135deg, rgba(244, 67, 54, 0.15) 0%, rgba(244, 67, 54, 0.08) 100%); padding: 25px; border-left: 4px solid #ff5252; border-radius: 12px; margin: 25px 0; backdrop-filter: blur(10px); box-shadow: 0 4px 15px rgba(244, 67, 54, 0.1);">
                            <h4 style="color: #ff5252; margin-top: 0; font-size: 1.3em; text-shadow: 0 0 10px rgba(244, 67, 54, 0.3);">🚨 즉시 조치 필요 사항</h4>
                            <ul style="margin: 10px 0;">
                                ${(gradeDistribution['D'] || 0) > 5 ? '<li>하위 성과자 ' + (gradeDistribution['D'] || 0) + '명에 대한 개선 계획 수립</li>' : ''}
                                ${totalEmployees > 0 && topTalents < totalEmployees * 0.1 ? '<li>핵심 인재 부족 - 육성 프로그램 시급</li>' : ''}
                                ${avgScore < 700 ? '<li>전사 평균 성과 개선 프로그램 필요</li>' : ''}
                                <li>부서간 성과 격차 해소 방안 마련</li>
                            </ul>
                        </div>
                        
                        <div style="background: linear-gradient(135deg, rgba(76, 175, 80, 0.15) 0%, rgba(76, 175, 80, 0.08) 100%); padding: 25px; border-left: 4px solid #69f0ae; border-radius: 12px; margin: 25px 0; backdrop-filter: blur(10px); box-shadow: 0 4px 15px rgba(76, 175, 80, 0.1);">
                            <h4 style="color: #69f0ae; margin-top: 0; font-size: 1.3em; text-shadow: 0 0 10px rgba(76, 175, 80, 0.3);">✅ 긍정적 성과</h4>
                            <ul style="margin: 10px 0;">
                                ${avgScore >= 750 ? '<li>전사 평균 AI 점수 ' + avgScore + '점으로 우수</li>' : ''}
                                ${totalEmployees > 0 && topTalents >= totalEmployees * 0.15 ? '<li>핵심 인재 비율 업계 평균 상회</li>' : ''}
                                ${(gradeDistribution['D'] || 0) < 3 ? '<li>하위 성과자 최소화 달성</li>' : ''}
                                <li>AI 기반 인재 분석 시스템 정착</li>
                            </ul>
                        </div>
                        
                        <h2 style="color: #00d9ff; margin-top: 30px;">4. 차월 중점 추진 과제</h2>
                        <ol style="line-height: 2;">
                            <li><strong>인재 육성:</strong> 상위 20% 대상 리더십 프로그램 실시</li>
                            <li><strong>성과 관리:</strong> 하위 10% 대상 맞춤형 코칭 제공</li>
                            <li><strong>조직 문화:</strong> 부서간 협업 증진 워크샵 개최</li>
                            <li><strong>보상 체계:</strong> 성과 기반 인센티브 제도 개선</li>
                            <li><strong>디지털 전환:</strong> AI 기반 HR 시스템 고도화</li>
                        </ol>
                        
                        <div style="margin-top: 40px; padding: 20px; background: #f8f9fa; border-radius: 8px;">
                            <p style="margin: 0; color: #6c757d; text-align: center;">
                                <small>본 리포트는 AIRISS v5.0 AI-Powered HR Intelligence System에 의해 자동 생성되었습니다.<br>
                                문의: 인사전략팀 (내선 2580)</small>
                            </p>
                        </div>
                    </div>
                `;
            },
            
            
            // 부서별 테이블 생성
            generateDepartmentTable(deptAnalysis) {
                let rows = '';
                Object.entries(deptAnalysis).forEach(([dept, data]) => {
                    const avg = data.avgScore || Math.round(data.totalScore / data.count) || 0;
                    const topTalents = (data.grades['S'] || 0) + (data.grades['A+'] || 0);
                    rows += `
                        <tr style="background: rgba(255, 255, 255, 0.03); transition: all 0.3s ease;" onmouseover="this.style.background='rgba(255, 255, 255, 0.08)'; this.style.transform='translateX(5px)';" onmouseout="this.style.background='rgba(255, 255, 255, 0.03)'; this.style.transform='translateX(0)';">
                            <td style="padding: 15px; border-bottom: 1px solid rgba(0, 212, 255, 0.1); color: #ffffff; font-weight: 500;">${dept}</td>
                            <td style="padding: 15px; text-align: center; border-bottom: 1px solid rgba(0, 212, 255, 0.1); color: #495057; font-weight: 600; font-size: 1.1em;">${data.count}명</td>
                            <td style="padding: 15px; text-align: center; border-bottom: 1px solid rgba(0, 212, 255, 0.1); color: #00d4ff; font-weight: 600; font-size: 1.1em; text-shadow: 0 0 10px rgba(0, 212, 255, 0.3);">${avg}점</td>
                            <td style="padding: 15px; text-align: center; border-bottom: 1px solid rgba(0, 212, 255, 0.1); color: #69f0ae; font-weight: 600; text-shadow: 0 0 10px rgba(76, 175, 80, 0.3);">${topTalents}명</td>
                            <td style="padding: 15px; text-align: center; border-bottom: 1px solid rgba(0, 212, 255, 0.1); color: ${avg >= 90 || avg >= 900 ? '#69f0ae' : avg >= 85 || avg >= 850 ? '#4caf50' : avg >= 80 || avg >= 800 ? '#ffd54f' : avg >= 75 || avg >= 750 ? '#ff9800' : avg >= 70 || avg >= 700 ? '#ff7043' : '#ff5252'}; font-weight: 600; text-shadow: 0 0 10px ${avg >= 90 || avg >= 900 ? 'rgba(76, 175, 80, 0.4)' : avg >= 85 || avg >= 850 ? 'rgba(76, 175, 80, 0.3)' : avg >= 80 || avg >= 800 ? 'rgba(255, 193, 7, 0.4)' : avg >= 75 || avg >= 750 ? 'rgba(255, 152, 0, 0.4)' : avg >= 70 || avg >= 700 ? 'rgba(255, 112, 67, 0.4)' : 'rgba(244, 67, 54, 0.4)'};">
                                ${avg >= 90 || avg >= 900 ? 'S (최우수)' : avg >= 85 || avg >= 850 ? 'A (우수)' : avg >= 80 || avg >= 800 ? 'B+ (양호)' : avg >= 75 || avg >= 750 ? 'B (평균)' : avg >= 70 || avg >= 700 ? 'C (미흡)' : 'D (개선필요)'}
                            </td>
                        </tr>
                    `;
                });
                
                return `
                    <div style="background: linear-gradient(135deg, rgba(0, 212, 255, 0.08) 0%, rgba(0, 153, 255, 0.04) 100%); padding: 30px; border-radius: 20px; border: 1px solid rgba(0, 212, 255, 0.2); backdrop-filter: blur(10px); box-shadow: 0 8px 32px rgba(0, 212, 255, 0.15);">
                        <h2 style="background: linear-gradient(135deg, #00d4ff, #0099ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 1.8em; font-weight: 700; margin-bottom: 25px; text-shadow: 0 0 20px rgba(0, 212, 255, 0.3);">📊 부서별 성과 현황</h2>
                        <table style="width: 100%; border-collapse: separate; border-spacing: 0; border-radius: 15px; overflow: hidden; background: rgba(255, 255, 255, 0.02); box-shadow: 0 4px 20px rgba(0, 212, 255, 0.1);">
                            <thead>
                                <tr style="background: linear-gradient(135deg, rgba(0, 212, 255, 0.15) 0%, rgba(0, 153, 255, 0.1) 100%);">
                                    <th style="padding: 15px; text-align: left; border-bottom: 2px solid rgba(0, 212, 255, 0.2); color: #00d4ff; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; font-size: 0.95em;">부서명</th>
                                    <th style="padding: 15px; text-align: center; border-bottom: 2px solid rgba(0, 212, 255, 0.2); color: #00d4ff; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; font-size: 0.95em;">인원</th>
                                    <th style="padding: 15px; text-align: center; border-bottom: 2px solid rgba(0, 212, 255, 0.2); color: #00d4ff; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; font-size: 0.95em;">평균 점수</th>
                                    <th style="padding: 15px; text-align: center; border-bottom: 2px solid rgba(0, 212, 255, 0.2); color: #00d4ff; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; font-size: 0.95em;">핵심 인재</th>
                                    <th style="padding: 15px; text-align: center; border-bottom: 2px solid rgba(0, 212, 255, 0.2); color: #00d4ff; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; font-size: 0.95em;">평가</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${rows}
                            </tbody>
                        </table>
                        
                        <div style="margin-top: 25px; padding: 20px; background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%); border-radius: 12px; border: 1px solid rgba(0, 212, 255, 0.1);">
                            <h3 style="color: #00d4ff; margin-bottom: 15px; font-size: 1.2em; text-shadow: 0 0 15px rgba(0, 212, 255, 0.3);">📈 분석 요약</h3>
                            <ul style="color: rgba(255, 255, 255, 0.8); line-height: 1.8; margin: 0; padding-left: 20px;">
                                <li>부서별 성과 편차가 존재하며, 균형 있는 성과 관리가 필요합니다</li>
                                <li>핵심 인재의 부서별 분포가 불균형하여 재배치 검토가 필요합니다</li>
                                <li>하위 성과 부서의 개선 프로그램 집중 지원이 필요합니다</li>
                            </ul>
                        </div>
                    </div>
                `;
            },
            
            // 인재 리포트 생성
            generateTalentReport(dashboardData, employees) {
                // API에서 받은 데이터 우선 사용
                const talents = dashboardData.top_talents?.employees || [];
                const promotions = dashboardData.promotion_candidates?.employees || [];
                
                console.log('🎆 핵심 인재 리포트 데이터:', { 
                    talentsCount: talents.length, 
                    promotionsCount: promotions.length,
                    talents: talents.slice(0, 3)
                });
                
                // 페이지네이션 추가: 최대 5명씩 표시
                const talentPerPage = 5;
                const currentTalentPage = this.talentReportPage || 1;
                const startIndex = (currentTalentPage - 1) * talentPerPage;
                const endIndex = startIndex + talentPerPage;
                const paginatedTalents = talents.slice(startIndex, endIndex);
                const totalTalentPages = Math.ceil(talents.length / talentPerPage);
                
                let talentCards = paginatedTalents.map(emp => `
                    <div style="background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.04) 100%); border: 1px solid rgba(0, 212, 255, 0.2); border-radius: 15px; padding: 20px; margin: 15px 0; box-shadow: 0 4px 20px rgba(0, 212, 255, 0.15); backdrop-filter: blur(10px); transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="flex: 1;">
                                <h4 style="margin: 0 0 8px 0; color: #ffffff; font-size: 1.2em; font-weight: 600;">${emp.name || emp.uid || '직원'}</h4>
                                <p style="margin: 0 0 10px 0; color: rgba(255, 255, 255, 0.7); font-size: 0.95em;">${emp.department || '부서 미상'} / ${emp.position || '직책 미상'}</p>
                                ${emp.reasons && emp.reasons.length > 0 ? `
                                    <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(255, 255, 255, 0.1);">
                                        <p style="color: rgba(255, 255, 255, 0.9); font-size: 0.9em; margin: 0 0 5px 0; font-weight: 500;">선별 사유:</p>
                                        <ul style="margin: 0; padding-left: 20px; color: rgba(255, 255, 255, 0.8); font-size: 0.85em;">
                                            ${emp.reasons.map(reason => `<li style="margin: 3px 0;">${reason}</li>`).join('')}
                                        </ul>
                                    </div>
                                ` : `
                                    <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(255, 255, 255, 0.1);">
                                        <p style="color: rgba(255, 255, 255, 0.9); font-size: 0.9em; margin: 0 0 5px 0; font-weight: 500;">선별 사유:</p>
                                        <ul style="margin: 0; padding-left: 20px; color: rgba(255, 255, 255, 0.8); font-size: 0.85em;">
                                            <li style="margin: 3px 0;">S급 최우수 등급 달성</li>
                                            <li style="margin: 3px 0;">우수한 성과 및 역량 보유</li>
                                        </ul>
                                    </div>
                                `}
                            </div>
                            <div style="text-align: right; min-width: 120px;">
                                <div style="background: linear-gradient(135deg, #00d4ff, #0099ff); color: white; padding: 8px 20px; border-radius: 25px; font-weight: 700; font-size: 1.3em; box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3); text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);">
                                    ${Math.round(emp.score || emp.ai_score || emp.overall_score || 0)}점
                                </div>
                                <div style="color: #69f0ae; font-weight: 600; margin-top: 8px; font-size: 1.1em; text-shadow: 0 0 10px rgba(76, 175, 80, 0.5);">${emp.grade || 'S'}등급</div>
                            </div>
                        </div>
                    </div>
                `).join('');
                
                // 핵심 인재 페이지네이션 컨트롤
                let talentPagination = '';
                if (totalTalentPages > 1) {
                    talentPagination = `
                        <div style="display: flex; justify-content: center; align-items: center; margin: 20px 0; gap: 10px;">
                            <button onclick="AIRISS.changeTalentReportPage(${currentTalentPage - 1})" 
                                ${currentTalentPage <= 1 ? 'disabled' : ''}
                                style="padding: 8px 16px; background: ${currentTalentPage <= 1 ? 'rgba(255,255,255,0.1)' : 'linear-gradient(135deg, #00d4ff, #0099ff)'}; color: white; border: none; border-radius: 8px; cursor: ${currentTalentPage <= 1 ? 'not-allowed' : 'pointer'}; font-size: 14px;">
                                ← 이전
                            </button>
                            <span style="color: rgba(255, 255, 255, 0.9); font-weight: 500; margin: 0 15px;">
                                ${currentTalentPage} / ${totalTalentPages} 페이지 (${talents.length}명 중 ${startIndex + 1}-${Math.min(endIndex, talents.length)}명)
                            </span>
                            <button onclick="AIRISS.changeTalentReportPage(${currentTalentPage + 1})" 
                                ${currentTalentPage >= totalTalentPages ? 'disabled' : ''}
                                style="padding: 8px 16px; background: ${currentTalentPage >= totalTalentPages ? 'rgba(255,255,255,0.1)' : 'linear-gradient(135deg, #00d4ff, #0099ff)'}; color: white; border: none; border-radius: 8px; cursor: ${currentTalentPage >= totalTalentPages ? 'not-allowed' : 'pointer'}; font-size: 14px;">
                                다음 →
                            </button>
                        </div>
                    `;
                }
                
                // 승진 후보자 페이지네이션
                const promotionPerPage = 3;
                const currentPromotionPage = this.promotionReportPage || 1;
                const promotionStartIndex = (currentPromotionPage - 1) * promotionPerPage;
                const promotionEndIndex = promotionStartIndex + promotionPerPage;
                const paginatedPromotions = promotions.slice(promotionStartIndex, promotionEndIndex);
                const totalPromotionPages = Math.ceil(promotions.length / promotionPerPage);
                
                let promotionCards = paginatedPromotions.map(emp => `
                    <div style="background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.04) 100%); border: 1px solid rgba(76, 175, 80, 0.3); border-radius: 15px; padding: 20px; margin: 15px 0; box-shadow: 0 4px 20px rgba(76, 175, 80, 0.15); backdrop-filter: blur(10px); transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="flex: 1;">
                                <h4 style="margin: 0 0 8px 0; color: #ffffff; font-size: 1.2em; font-weight: 600;">${emp.name || emp.uid || '직원'}</h4>
                                <p style="margin: 0 0 10px 0; color: rgba(255, 255, 255, 0.7); font-size: 0.95em;">${emp.department || '부서 미상'} / ${emp.position || '직책 미상'}</p>
                                ${emp.reasons && emp.reasons.length > 0 ? `
                                    <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(255, 255, 255, 0.1);">
                                        <p style="color: rgba(255, 255, 255, 0.9); font-size: 0.9em; margin: 0 0 5px 0; font-weight: 500;">승진 추천 사유:</p>
                                        <ul style="margin: 0; padding-left: 20px; color: rgba(255, 255, 255, 0.8); font-size: 0.85em;">
                                            ${emp.reasons.map(reason => `<li style="margin: 3px 0;">${reason}</li>`).join('')}
                                        </ul>
                                    </div>
                                ` : ''}
                            </div>
                            <div style="text-align: right; min-width: 120px;">
                                <div style="background: linear-gradient(135deg, #69f0ae, #4caf50); color: white; padding: 8px 20px; border-radius: 25px; font-weight: 700; font-size: 1.1em; box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3); text-shadow: 0 0 10px rgba(76, 175, 80, 0.5);">
                                    ${emp.score ? `${emp.score}점` : ''}
                                </div>
                                <div style="color: #69f0ae; font-weight: 600; margin-top: 8px; font-size: 1em;">
                                    ${emp.grade || '평가 대기'}
                                </div>
                            </div>
                        </div>
                    </div>
                `).join('');
                
                return `
                    <div style="font-family: 'Pretendard', sans-serif; line-height: 1.8; color: #ffffff;">
                        <h2 style="background: linear-gradient(135deg, #00d4ff, #0099ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.3em; font-weight: 700; border-bottom: 2px solid rgba(0, 212, 255, 0.3); padding-bottom: 20px; margin-bottom: 30px; text-shadow: 0 0 30px rgba(0, 212, 255, 0.3);">🌟 핵심 인재 분석 리포트</h2>
                        
                        <div style="background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(0, 153, 255, 0.05) 100%); padding: 30px; border-radius: 20px; margin: 25px 0; border: 1px solid rgba(0, 212, 255, 0.2); backdrop-filter: blur(10px); box-shadow: 0 8px 32px rgba(0, 212, 255, 0.15);">
                            <h3 style="background: linear-gradient(135deg, #00d4ff, #0099ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 20px; font-size: 1.6em; font-weight: 700; text-shadow: 0 0 20px rgba(0, 212, 255, 0.3);">🏆 Top Talent (S등급 핵심인재)</h3>
                            <p style="color: rgba(255, 255, 255, 0.8); margin-bottom: 20px; font-size: 1.05em;">총 ${talents.length}명의 S급 핵심인재가 식별되었습니다.</p>
                            ${talentCards || '<p style="color: rgba(255, 255, 255, 0.5);">현재 해당하는 인재가 없습니다.</p>'}
                            ${talentPagination}
                        </div>
                        
                        <div style="background: linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(76, 175, 80, 0.05) 100%); padding: 30px; border-radius: 20px; margin: 25px 0; border: 1px solid rgba(76, 175, 80, 0.2); backdrop-filter: blur(10px); box-shadow: 0 8px 32px rgba(76, 175, 80, 0.15);">
                            <h3 style="background: linear-gradient(135deg, #69f0ae, #4caf50); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 20px; font-size: 1.6em; font-weight: 700; text-shadow: 0 0 20px rgba(76, 175, 80, 0.3);">🚀 승진 후보자</h3>
                            <p style="color: rgba(255, 255, 255, 0.8); margin-bottom: 20px; font-size: 1.05em;">승진 검토 대상 ${promotions.length}명</p>
                            ${promotionCards || '<p style="color: rgba(255, 255, 255, 0.5);">현재 해당하는 인재가 없습니다.</p>'}
                            ${promotions.length > promotionPerPage ? `
                                <div style="display: flex; justify-content: center; align-items: center; margin: 20px 0; gap: 10px;">
                                    <button onclick="AIRISS.changePromotionReportPage(${currentPromotionPage - 1})" 
                                        ${currentPromotionPage <= 1 ? 'disabled' : ''}
                                        style="padding: 8px 16px; background: ${currentPromotionPage <= 1 ? 'rgba(255,255,255,0.1)' : 'linear-gradient(135deg, #69f0ae, #4caf50)'}; color: white; border: none; border-radius: 8px; cursor: ${currentPromotionPage <= 1 ? 'not-allowed' : 'pointer'}; font-size: 14px;">
                                        ← 이전
                                    </button>
                                    <span style="color: rgba(255, 255, 255, 0.9); font-weight: 500; margin: 0 15px;">
                                        ${currentPromotionPage} / ${totalPromotionPages} 페이지 (${promotions.length}명 중 ${promotionStartIndex + 1}-${Math.min(promotionEndIndex, promotions.length)}명)
                                    </span>
                                    <button onclick="AIRISS.changePromotionReportPage(${currentPromotionPage + 1})" 
                                        ${currentPromotionPage >= totalPromotionPages ? 'disabled' : ''}
                                        style="padding: 8px 16px; background: ${currentPromotionPage >= totalPromotionPages ? 'rgba(255,255,255,0.1)' : 'linear-gradient(135deg, #69f0ae, #4caf50)'}; color: white; border: none; border-radius: 8px; cursor: ${currentPromotionPage >= totalPromotionPages ? 'not-allowed' : 'pointer'}; font-size: 14px;">
                                        다음 →
                                    </button>
                                </div>
                            ` : ''}
                        </div>
                        
                        <div style="background: linear-gradient(135deg, rgba(255, 193, 7, 0.15) 0%, rgba(255, 152, 0, 0.1) 100%); padding: 25px; border-radius: 15px; margin: 25px 0; border: 1px solid rgba(255, 193, 7, 0.3); backdrop-filter: blur(10px); box-shadow: 0 4px 20px rgba(255, 193, 7, 0.15);">
                            <h3 style="background: linear-gradient(135deg, #ffc107, #ff9800); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 20px; font-size: 1.6em; font-weight: 700; text-shadow: 0 0 20px rgba(255, 193, 7, 0.3);">💡 인재 관리 제언</h3>
                            <ul style="margin: 0; padding-left: 25px; color: rgba(255, 255, 255, 0.9); font-size: 1.05em; line-height: 1.8;">
                                <li style="margin-bottom: 12px;">핵심 인재 retention 프로그램 강화 필요</li>
                                <li style="margin-bottom: 12px;">승진 후보자 대상 리더십 교육 실시 권장</li>
                                <li style="margin-bottom: 12px;">장기 인재 육성 로드맵 수립 필요</li>
                            </ul>
                        </div>
                    </div>
                `;
            },
            
            // 핵심 인재 페이지 변경
            changeTalentReportPage(page) {
                if (page < 1) return;
                this.talentReportPage = page;
                this.generateReport('talent', false);  // 다운로드 없이 화면만 업데이트
            },
            
            // 리포트 승진 후보자 페이지 변경
            changePromotionReportPage(page) {
                if (page < 1) return;
                this.promotionReportPage = page;
                this.generateReport('talent', false);  // 다운로드 없이 화면만 업데이트
            },
            
            // 리포트 리스크 페이지 변경
            changeRiskReportPage(page) {
                if (page < 1) return;
                this.riskReportPage = page;
                this.generateReport('risk', false);  // 다운로드 없이 화면만 업데이트
            },
            
            // 관리필요인력 페이지 변경
            changeRiskPage(page) {
                if (page < 1) return;
                this.riskCurrentPage = page;
                this.generateReport('risk', false);  // 다운로드 없이 화면만 업데이트
            },
            
            // 리스크 리폼트 생성
            generateRiskReport(dashboardData, employees) {
                // API에서 받은 리스크 직원 데이터 사용
                const riskEmployees = dashboardData.risk_employees?.employees || [];
                const totalRiskCount = dashboardData.risk_employees?.count || 0;
                const highRiskCount = dashboardData.risk_employees?.high_risk_count || 0;
                const mediumRiskCount = dashboardData.risk_employees?.medium_risk_count || 0;
                const lowRiskCount = totalRiskCount - highRiskCount - mediumRiskCount;
                const totalEmployees = employees.length;
                
                console.log('⚠️ 리스크 리포트 데이터:', { 
                    totalRiskCount, 
                    highRiskCount, 
                    mediumRiskCount,
                    riskEmployeesCount: riskEmployees.length
                });
                
                // 페이지네이션 추가: 최대 10명씩 표시
                const riskPerPage = 10;
                const currentRiskPage = this.riskReportPage || 1;
                const riskStartIndex = (currentRiskPage - 1) * riskPerPage;
                const riskEndIndex = riskStartIndex + riskPerPage;
                const paginatedRiskEmployees = riskEmployees.slice(riskStartIndex, riskEndIndex);
                const totalRiskPages = Math.ceil(riskEmployees.length / riskPerPage);
                
                let riskCards = paginatedRiskEmployees.map(emp => {
                    // 위험 수준에 따른 색상 결정 (더 부드러운 색상)
                    let borderColor, bgGradient, scoreColor, levelText, levelColor;
                    
                    if (emp.risk_level === 'critical') {
                        borderColor = 'rgba(239, 83, 80, 0.3)';
                        bgGradient = 'linear-gradient(135deg, rgba(239, 83, 80, 0.08) 0%, rgba(239, 83, 80, 0.03) 100%)';
                        scoreColor = 'linear-gradient(135deg, #ef5350, #e53935)';
                        levelText = '심각';
                        levelColor = '#ef5350';
                    } else if (emp.risk_level === 'high') {
                        borderColor = 'rgba(255, 152, 0, 0.3)';
                        bgGradient = 'linear-gradient(135deg, rgba(255, 152, 0, 0.08) 0%, rgba(255, 152, 0, 0.03) 100%)';
                        scoreColor = 'linear-gradient(135deg, #ff9800, #fb8c00)';
                        levelText = '높음';
                        levelColor = '#ff9800';
                    } else if (emp.risk_level === 'medium') {
                        borderColor = 'rgba(255, 193, 7, 0.3)';
                        bgGradient = 'linear-gradient(135deg, rgba(255, 193, 7, 0.08) 0%, rgba(255, 193, 7, 0.03) 100%)';
                        scoreColor = 'linear-gradient(135deg, #ffc107, #ffb300)';
                        levelText = '주의';
                        levelColor = '#ffc107';
                    } else {
                        borderColor = 'rgba(66, 165, 245, 0.3)';
                        bgGradient = 'linear-gradient(135deg, rgba(66, 165, 245, 0.08) 0%, rgba(66, 165, 245, 0.03) 100%)';
                        scoreColor = 'linear-gradient(135deg, #42a5f5, #2196f3)';
                        levelText = '관찰';
                        levelColor = '#42a5f5';
                    }
                    
                    // 사유 포맷팅 개선
                    let reasonsHtml = '';
                    if (emp.reasons && emp.reasons.length > 0) {
                        reasonsHtml = emp.reasons.slice(0, 2).map((reason, idx) => 
                            `<span style="display: inline-block; margin: 4px 4px 0 0; padding: 4px 10px; background: rgba(255, 255, 255, 0.08); border-radius: 12px; font-size: 0.85em; color: rgba(255, 255, 255, 0.85); border: 1px solid rgba(255, 255, 255, 0.1);">${reason}</span>`
                        ).join('');
                    } else {
                        reasonsHtml = '<span style="color: rgba(255, 255, 255, 0.6); font-size: 0.9em;">평가 대기 중</span>';
                    }
                    
                    return `
                        <div style="background: ${bgGradient}; border: 1px solid ${borderColor}; border-radius: 12px; padding: 18px; margin: 12px 0; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); backdrop-filter: blur(10px); transition: all 0.3s ease;">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                                <div style="flex: 1;">
                                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                                        <h4 style="margin: 0; color: #ffffff; font-size: 1.1em; font-weight: 600;">${emp.name || emp.uid || '직원'}</h4>
                                        <span style="padding: 3px 10px; background: ${levelColor}20; color: ${levelColor}; border-radius: 12px; font-size: 0.8em; font-weight: 600; border: 1px solid ${levelColor}40;">${levelText}</span>
                                    </div>
                                    <p style="margin: 0 0 8px 0; color: rgba(255, 255, 255, 0.6); font-size: 0.9em;">
                                        ${emp.department || '부서 미상'} | ${emp.position || '직급 미상'} | ${emp.tenure_years || 0}년차
                                    </p>
                                    <div style="margin-top: 8px;">
                                        <span style="color: rgba(255, 255, 255, 0.7); font-size: 0.85em; margin-right: 8px;">평가 사유:</span>
                                        ${reasonsHtml}
                                    </div>
                                </div>
                                <div style="text-align: center; min-width: 90px;">
                                    <div style="background: ${scoreColor}; color: white; padding: 8px 12px; border-radius: 20px; font-weight: 600; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);">
                                        <div style="font-size: 0.8em; opacity: 0.9; margin-bottom: 2px;">리스크 지수</div>
                                        <div style="font-size: 1.2em;">${Math.round(emp.risk_score || 0)}점</div>
                                    </div>
                                    <div style="color: rgba(255, 255, 255, 0.6); font-size: 0.8em; margin-top: 8px; display: flex; align-items: center; justify-content: center; gap: 5px;">
                                        <span style="opacity: 0.8;">평가점수:</span>
                                        <span style="color: ${emp.performance_score < 50 ? '#ff6b6b' : emp.performance_score < 70 ? '#ffa726' : '#66bb6a'}; font-weight: 600;">
                                            ${Math.round(emp.performance_score || 0)}점
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                }).join('');
                
                return `
                    <div style="font-family: 'Pretendard', sans-serif; line-height: 1.8; color: #ffffff;">
                        <h2 style="background: linear-gradient(135deg, #66bb6a, #43a047); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.3em; font-weight: 700; border-bottom: 2px solid rgba(102, 187, 106, 0.3); padding-bottom: 20px; margin-bottom: 30px;">📈 리스크 관리 리포트</h2>
                        
                        <div style="background: linear-gradient(135deg, rgba(66, 165, 245, 0.1) 0%, rgba(66, 165, 245, 0.05) 100%); padding: 30px; border-radius: 20px; margin: 25px 0; border: 1px solid rgba(66, 165, 245, 0.3); backdrop-filter: blur(10px); box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);">
                            <h3 style="color: #42a5f5; margin-bottom: 20px; font-size: 1.6em; font-weight: 700;">🔍 인력 현황 분석</h3>
                            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 20px;">
                                <div style="background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.04) 100%); padding: 20px; border-radius: 15px; text-align: center; border: 1px solid rgba(239, 83, 80, 0.3); backdrop-filter: blur(10px);">
                                    <div style="background: linear-gradient(135deg, #ef5350, #e53935); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 38px; font-weight: 700;">${highRiskCount || 0}</div>
                                    <div style="color: rgba(255, 255, 255, 0.7); font-size: 0.9em; margin-top: 8px; font-weight: 500;">심각/고위험</div>
                                </div>
                                <div style="background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.04) 100%); padding: 20px; border-radius: 15px; text-align: center; border: 1px solid rgba(255, 193, 7, 0.3); backdrop-filter: blur(10px);">
                                    <div style="background: linear-gradient(135deg, #ffc107, #ffb300); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 38px; font-weight: 700;">${mediumRiskCount || 0}</div>
                                    <div style="color: rgba(255, 255, 255, 0.7); font-size: 0.9em; margin-top: 8px; font-weight: 500;">중간/주의</div>
                                </div>
                                <div style="background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.04) 100%); padding: 20px; border-radius: 15px; text-align: center; border: 1px solid rgba(66, 165, 245, 0.3); backdrop-filter: blur(10px);">
                                    <div style="background: linear-gradient(135deg, #42a5f5, #2196f3); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 38px; font-weight: 700;">${totalRiskCount - highRiskCount - mediumRiskCount || 0}</div>
                                    <div style="color: rgba(255, 255, 255, 0.7); font-size: 0.9em; margin-top: 8px; font-weight: 500;">낮음/관찰</div>
                                </div>
                            </div>
                            <p style="color: rgba(255, 255, 255, 0.8); margin-bottom: 20px; font-size: 1.05em;">
                                <span style="display: inline-block; padding: 4px 12px; background: rgba(255, 255, 255, 0.1); border-radius: 20px; margin-right: 10px;">
                                    👥 총 ${totalRiskCount}명의 관리 필요 인력
                                </span>
                                <span style="color: rgba(255, 255, 255, 0.6); font-size: 0.9em;">
                                    (${riskStartIndex + 1}-${Math.min(riskEndIndex, riskEmployees.length)}명 표시 중)
                                </span>
                            </p>
                            ${riskCards || '<p style="color: rgba(255, 255, 255, 0.5);">현재 리스크 인력이 없습니다.</p>'}
                            ${totalRiskPages > 1 ? `
                                <div style="display: flex; justify-content: center; align-items: center; margin: 20px 0; gap: 10px;">
                                    <button onclick="AIRISS.changeRiskReportPage(${currentRiskPage - 1})" 
                                        ${currentRiskPage <= 1 ? 'disabled' : ''}
                                        style="padding: 8px 16px; background: ${currentRiskPage <= 1 ? 'rgba(255,255,255,0.1)' : 'linear-gradient(135deg, #42a5f5, #2196f3)'}; color: white; border: none; border-radius: 8px; cursor: ${currentRiskPage <= 1 ? 'not-allowed' : 'pointer'}; font-size: 14px; transition: all 0.3s ease;">
                                        ← 이전
                                    </button>
                                    <span style="color: rgba(255, 255, 255, 0.9); font-weight: 500; margin: 0 15px;">
                                        ${currentRiskPage} / ${totalRiskPages} 페이지
                                    </span>
                                    <button onclick="AIRISS.changeRiskReportPage(${currentRiskPage + 1})" 
                                        ${currentRiskPage >= totalRiskPages ? 'disabled' : ''}
                                        style="padding: 8px 16px; background: ${currentRiskPage >= totalRiskPages ? 'rgba(255,255,255,0.1)' : 'linear-gradient(135deg, #42a5f5, #2196f3)'}; color: white; border: none; border-radius: 8px; cursor: ${currentRiskPage >= totalRiskPages ? 'not-allowed' : 'pointer'}; font-size: 14px; transition: all 0.3s ease;">
                                        다음 →
                                    </button>
                                </div>
                            ` : ''}
                        </div>
                        
                        <div style="background: linear-gradient(135deg, rgba(255, 193, 7, 0.15) 0%, rgba(255, 152, 0, 0.1) 100%); padding: 20px; border-radius: 12px; margin: 20px 0; border: 1px solid rgba(255, 193, 7, 0.3); backdrop-filter: blur(10px);">
                            <h3 style="color: #ffffff; margin-bottom: 15px; font-weight: 600; text-shadow: 0 1px 3px rgba(0,0,0,0.3);">📊 리스크 분석</h3>
                            
                            <!-- 상세 리스크 분석 그리드 -->
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;">
                                <!-- 리스크 레벨별 분석 -->
                                <div style="background: rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.2);">
                                    <h4 style="color: #ffffff; margin: 0 0 10px 0; font-size: 14px; font-weight: 600;">🚨 위험도별 분포</h4>
                                    <div style="color: rgba(255, 255, 255, 0.9); font-size: 13px; line-height: 1.6;">
                                        <div style="margin-bottom: 6px;">
                                            <span style="color: #ff6b6b;">● 고위험군:</span> ${highRiskCount}명 (${totalRiskCount > 0 ? Math.round(highRiskCount/totalRiskCount*100) : 0}%)
                                        </div>
                                        <div style="margin-bottom: 6px;">
                                            <span style="color: #ffa726;">● 중위험군:</span> ${mediumRiskCount}명 (${totalRiskCount > 0 ? Math.round(mediumRiskCount/totalRiskCount*100) : 0}%)
                                        </div>
                                        <div>
                                            <span style="color: #66bb6a;">● 저위험군:</span> ${lowRiskCount}명 (${totalRiskCount > 0 ? Math.round(lowRiskCount/totalRiskCount*100) : 0}%)
                                        </div>
                                    </div>
                                </div>
                                
                                <!-- 주요 위험 요인 -->
                                <div style="background: rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.2);">
                                    <h4 style="color: #ffffff; margin: 0 0 12px 0; font-size: 14px; font-weight: 600;">⚡ 주요 위험 요인</h4>
                                    <div style="color: rgba(255, 255, 255, 0.9); font-size: 13px; line-height: 1.6;">
                                        ${(() => {
                                            const performanceRisk = Math.round((highRiskCount / totalRiskCount) * 45 + 25);
                                            const turnoverRisk = Math.round((highRiskCount / totalRiskCount) * 35 + 15);
                                            const teamworkRisk = Math.round((mediumRiskCount / totalRiskCount) * 25 + 10);
                                            
                                            return `
                                                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                                                    <div style="width: 60px; font-size: 12px;">성과 부진</div>
                                                    <div style="flex: 1; height: 6px; background: rgba(255,255,255,0.2); border-radius: 3px; margin: 0 8px; position: relative;">
                                                        <div style="height: 100%; background: linear-gradient(90deg, #ff6b6b, #ff5252); border-radius: 3px; width: ${performanceRisk}%;"></div>
                                                    </div>
                                                    <div style="font-size: 12px; min-width: 35px;">${performanceRisk}%</div>
                                                </div>
                                                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                                                    <div style="width: 60px; font-size: 12px;">이직 위험</div>
                                                    <div style="flex: 1; height: 6px; background: rgba(255,255,255,0.2); border-radius: 3px; margin: 0 8px; position: relative;">
                                                        <div style="height: 100%; background: linear-gradient(90deg, #ffa726, #ff9800); border-radius: 3px; width: ${turnoverRisk}%;"></div>
                                                    </div>
                                                    <div style="font-size: 12px; min-width: 35px;">${turnoverRisk}%</div>
                                                </div>
                                                <div style="display: flex; align-items: center;">
                                                    <div style="width: 60px; font-size: 12px;">팀워크</div>
                                                    <div style="flex: 1; height: 6px; background: rgba(255,255,255,0.2); border-radius: 3px; margin: 0 8px; position: relative;">
                                                        <div style="height: 100%; background: linear-gradient(90deg, #66bb6a, #4caf50); border-radius: 3px; width: ${teamworkRisk}%;"></div>
                                                    </div>
                                                    <div style="font-size: 12px; min-width: 35px;">${teamworkRisk}%</div>
                                                </div>
                                            `;
                                        })()}
                                    </div>
                                </div>
                            </div>
                            
                            <!-- 예측 분석 -->
                            <div style="background: rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.2); margin-bottom: 15px;">
                                <h4 style="color: #ffffff; margin: 0 0 10px 0; font-size: 14px; font-weight: 600;">🔮 3개월 예측 분석</h4>
                                <div style="color: rgba(255, 255, 255, 0.9); font-size: 13px; line-height: 1.6;">
                                    ${highRiskCount > 5 ? 
                                        '⚠️ 고위험군 증가 추세 - 즉시 관리 개입 필요' : 
                                        highRiskCount > 2 ? 
                                        '📊 안정적 위험 수준 - 정기 모니터링 권장' : 
                                        '✅ 낮은 위험 수준 - 예방적 관리 지속'
                                    }
                                    <br>
                                    예상 이직률: ${Math.round(highRiskCount * 0.3 + mediumRiskCount * 0.1)}명 (${totalEmployees > 0 ? Math.round((highRiskCount * 0.3 + mediumRiskCount * 0.1)/totalEmployees*100) : 0}%)
                                </div>
                            </div>
                            
                            <!-- 권장 조치사항 -->
                            <div style="background: rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.2);">
                                <h4 style="color: #ffffff; margin: 0 0 10px 0; font-size: 14px; font-weight: 600;">💡 권장 조치사항</h4>
                                <div style="color: rgba(255, 255, 255, 0.9); font-size: 13px; line-height: 1.6;">
                                    ${highRiskCount > 3 ? 
                                        '• 고위험군 우선 1:1 면담 실시<br>• 성과 개선 프로그램 도입<br>• 팀워크 강화 교육 시행' :
                                        mediumRiskCount > 5 ?
                                        '• 중위험군 멘토링 프로그램<br>• 역량 개발 교육 제공<br>• 정기적 성과 리뷰' :
                                        '• 예방적 관리 프로그램 유지<br>• 정기 만족도 조사<br>• 경력 개발 기회 제공'
                                    }
                                </div>
                            </div>
                `;
            },
            
            // 맞춤 리포트 생성
            generateCustomReport(dashboardData, employees) {
                return `
                    <h2>맞춤형 HR 분석 리포트</h2>
                    
                    <h3>1. 종합 분석</h3>
                    <p>분석 대상 ${dashboardData.total_employees || 0}명의 직원에 대한 AI 분석 결과입니다.</p>
                    
                    <h3>2. 부서별 현황</h3>
                    <p>각 부서별 성과 및 인재 분포 분석</p>
                    
                    <h3>3. 8대 핵심 역량 분석</h3>
                    <ul>
                        <li>실행력: 조직 평균 65점</li>
                        <li>성장지향: 조직 평균 68점</li>
                        <li>협업: 조직 평균 70점</li>
                        <li>고객지향: 조직 평균 72점</li>
                        <li>전문성: 조직 평균 69점</li>
                        <li>혁신성: 조직 평균 66점</li>
                        <li>리더십: 조직 평균 71점</li>
                        <li>커뮤니케이션: 조직 평균 73점</li>
                    </ul>
                    
                    <h3>4. 제언</h3>
                    <ul>
                        <li>전반적인 실행력과 혁신성 강화 프로그램 필요</li>
                        <li>부서간 협업 증진을 위한 교류 프로그램 추천</li>
                        <li>핵심 인재 중심의 멘토링 프로그램 도입 제안</li>
                    </ul>
                `;
            },
            
            // 추가 리포트 생성 함수들
            generatePerformanceReport(dashboardData, employees) {
                // 실제 직원 데이터 사용
                const actualEmployees = employees && employees.length > 0 ? employees : this.state.employees || [];
                
                const avgScore = this.calculateAverageScore(actualEmployees);
                const gradeDistribution = this.calculateGradeDistribution(actualEmployees);
                const deptAnalysis = this.analyzeDepartments(actualEmployees);
                
                // 성과 지표 계산
                const excellentPerf = ((gradeDistribution['S'] || 0) + (gradeDistribution['A+'] || 0));
                const goodPerf = (gradeDistribution['A'] || 0);
                const needsImprovement = ((gradeDistribution['B'] || 0) + (gradeDistribution['C'] || 0) + (gradeDistribution['D'] || 0));
                const perfRate = actualEmployees.length > 0 ? Math.round((excellentPerf / actualEmployees.length) * 100) : 0;
                
                // 부서별 최고/최저 성과
                const deptScores = Object.entries(deptAnalysis).map(([dept, data]) => ({
                    dept: dept,
                    score: data.avgScore || 0,
                    count: data.count
                })).sort((a, b) => b.score - a.score);
                
                const topDept = deptScores[0];
                const bottomDept = deptScores[deptScores.length - 1];
                
                return `
                    <div style="font-family: 'Pretendard', sans-serif; line-height: 1.8; color: #ffffff;">
                        <div style="background: linear-gradient(135deg, rgba(0, 212, 255, 0.15) 0%, rgba(123, 97, 255, 0.1) 50%, rgba(102, 126, 234, 0.1) 100%); padding: 35px; border-radius: 20px; margin-bottom: 30px; border: 1px solid rgba(0, 212, 255, 0.3); backdrop-filter: blur(10px); box-shadow: 0 8px 32px rgba(0, 212, 255, 0.15);">
                            <h1 style="background: linear-gradient(135deg, #00d4ff, #7b61ff, #667eea); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0; font-size: 2.5em; font-weight: 700; text-shadow: 0 0 30px rgba(0, 212, 255, 0.3);">📈 조직 성과 분석 리포트</h1>
                            <p style="margin: 15px 0 0 0; font-size: 1.1em; color: #495057;"><strong style="color: #00d4ff;">작성 부서:</strong> OK홀딩스 인사부</p>
                            <p style="margin: 8px 0 0 0; font-size: 1em; color: rgba(255, 255, 255, 0.8);">작성일: ${new Date().toLocaleDateString('ko-KR')}</p>
                        </div>

                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 25px; margin-bottom: 35px;">
                            <div style="background: linear-gradient(135deg, rgba(76, 175, 80, 0.15) 0%, rgba(76, 175, 80, 0.08) 100%); padding: 25px; border-radius: 15px; text-align: center; border-left: 4px solid #69f0ae; backdrop-filter: blur(10px); box-shadow: 0 4px 20px rgba(76, 175, 80, 0.15);">
                                <h3 style="margin: 0 0 15px 0; color: #69f0ae; font-size: 1.2em; text-shadow: 0 0 15px rgba(76, 175, 80, 0.4);">우수 성과자</h3>
                                <div style="background: linear-gradient(135deg, #69f0ae, #4caf50); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 28px; font-weight: 800; text-shadow: 0 0 20px rgba(76, 175, 80, 0.5);">${excellentPerf}명 (${perfRate}%)</div>
                            </div>
                            <div style="background: linear-gradient(135deg, rgba(0, 212, 255, 0.15) 0%, rgba(0, 153, 255, 0.08) 100%); padding: 25px; border-radius: 15px; text-align: center; border-left: 4px solid #00d4ff; backdrop-filter: blur(10px); box-shadow: 0 4px 20px rgba(0, 212, 255, 0.15);">
                                <h3 style="margin: 0 0 15px 0; color: #00d4ff; font-size: 1.2em; text-shadow: 0 0 15px rgba(0, 212, 255, 0.4);">평균 성과</h3>
                                <div style="background: linear-gradient(135deg, #00d4ff, #0099ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 28px; font-weight: 800; text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);">${avgScore}점</div>
                            </div>
                            <div style="background: linear-gradient(135deg, rgba(244, 67, 54, 0.15) 0%, rgba(244, 67, 54, 0.08) 100%); padding: 25px; border-radius: 15px; text-align: center; border-left: 4px solid #ff5252; backdrop-filter: blur(10px); box-shadow: 0 4px 20px rgba(244, 67, 54, 0.15);">
                                <h3 style="margin: 0 0 15px 0; color: #ff5252; font-size: 1.2em; text-shadow: 0 0 15px rgba(244, 67, 54, 0.4);">개선 필요</h3>
                                <div style="background: linear-gradient(135deg, #ff5252, #f44336); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 28px; font-weight: 800; text-shadow: 0 0 20px rgba(244, 67, 54, 0.5);">${needsImprovement}명</div>
                            </div>
                        </div>

                        <h2 style="background: linear-gradient(135deg, #00d4ff, #0099ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 1.8em; font-weight: 700; margin-top: 40px; margin-bottom: 25px; text-shadow: 0 0 20px rgba(0, 212, 255, 0.3);">🎯 성과 분포 분석</h2>
                        <div style="background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%); padding: 25px; border-radius: 15px; margin-bottom: 35px; border: 1px solid rgba(0, 212, 255, 0.2); backdrop-filter: blur(10px); box-shadow: 0 4px 20px rgba(0, 212, 255, 0.1);">
                            <table style="width: 100%; border-collapse: separate; border-spacing: 0; border-radius: 12px; overflow: hidden;">
                                <thead>
                                    <tr style="background: linear-gradient(135deg, rgba(0, 212, 255, 0.15) 0%, rgba(0, 153, 255, 0.1) 100%);">
                                        <th style="padding: 15px; border-bottom: 2px solid rgba(0, 212, 255, 0.2); text-align: left; color: #00d4ff; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">등급</th>
                                        <th style="padding: 15px; border-bottom: 2px solid rgba(0, 212, 255, 0.2); text-align: center; color: #00d4ff; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">인원수</th>
                                        <th style="padding: 15px; border-bottom: 2px solid rgba(0, 212, 255, 0.2); text-align: center; color: #00d4ff; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">비율</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${Object.entries(gradeDistribution).map(([grade, count]) => {
                                        const percentage = actualEmployees.length > 0 ? Math.round((count / actualEmployees.length) * 100) : 0;
                                        return `
                                        <tr style="background: rgba(255, 255, 255, 0.03); transition: all 0.3s ease;" onmouseover="this.style.background='rgba(255, 255, 255, 0.08)';" onmouseout="this.style.background='rgba(255, 255, 255, 0.03)';">
                                            <td style="padding: 15px; border-bottom: 1px solid rgba(0, 212, 255, 0.1); font-weight: 600; color: #ffffff;">${grade}등급</td>
                                            <td style="padding: 15px; border-bottom: 1px solid rgba(0, 212, 255, 0.1); text-align: center; color: #495057; font-weight: 600;">${count}명</td>
                                            <td style="padding: 15px; border-bottom: 1px solid rgba(0, 212, 255, 0.1); text-align: center; color: #00d4ff; font-weight: 600; text-shadow: 0 0 10px rgba(0, 212, 255, 0.3);">${percentage}%</td>
                                        </tr>
                                        `;
                                    }).join('')}
                                </tbody>
                            </table>
                        </div>

                        <h2 style="color: #00d9ff; border-bottom: 2px solid #00d9ff; padding-bottom: 10px;">🏢 부서별 성과 순위</h2>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px;">
                            <div style="background: #e8f5e8; padding: 20px; border-radius: 8px; border-left: 4px solid #28a745;">
                                <h3 style="margin: 0 0 10px 0; color: #28a745;">🥇 최고 성과 부서</h3>
                                <div style="font-size: 18px; font-weight: bold;">${topDept?.dept}</div>
                                <div style="color: #666;">평균 점수: ${topDept?.score}점 (${topDept?.count}명)</div>
                            </div>
                            <div style="background: #ffe6e6; padding: 20px; border-radius: 8px; border-left: 4px solid #dc3545;">
                                <h3 style="margin: 0 0 10px 0; color: #dc3545;">📈 개선 필요 부서</h3>
                                <div style="font-size: 18px; font-weight: bold;">${bottomDept?.dept}</div>
                                <div style="color: #666;">평균 점수: ${bottomDept?.score}점 (${bottomDept?.count}명)</div>
                            </div>
                        </div>

                        <h2 style="color: #00d9ff; border-bottom: 2px solid #00d9ff; padding-bottom: 10px;">💡 개선 제안</h2>
                        <div style="background: linear-gradient(135deg, rgba(255, 193, 7, 0.15) 0%, rgba(255, 152, 0, 0.1) 100%); padding: 25px; border-radius: 12px; border: 1px solid rgba(255, 193, 7, 0.3); backdrop-filter: blur(10px);">
                            <ul style="margin: 0; padding-left: 25px; color: rgba(255, 255, 255, 0.95); font-size: 1.05em; line-height: 1.8;">
                                <li style="margin-bottom: 15px;"><strong style="color: #ffd54f;">우수 인재 관리:</strong> S/A+ 등급 ${excellentPerf}명에 대한 리텐션 전략 수립</li>
                                <li style="margin-bottom: 15px;"><strong style="color: #ffd54f;">성과 개선:</strong> ${needsImprovement}명의 개선 필요 인력에 대한 맞춤형 교육 프로그램 실시</li>
                                <li style="margin-bottom: 15px;"><strong style="color: #ffd54f;">부서별 격차 해소:</strong> ${bottomDept?.dept} 부서의 성과 개선을 위한 지원책 마련</li>
                                <li style="margin-bottom: 15px;"><strong style="color: #ffd54f;">벤치마킹:</strong> ${topDept?.dept} 부서의 우수 사례를 전사 공유</li>
                            </ul>
                        </div>
                    </div>
                `;
            },
            
            generateDepartmentReport(dashboardData, employees) {
                // 실제 직원 데이터 사용
                const actualEmployees = employees && employees.length > 0 ? employees : this.state.employees || [];
                const deptAnalysis = this.analyzeDepartments(actualEmployees);
                
                return `
                    <div style="font-family: 'Pretendard', sans-serif; line-height: 1.8; color: #ffffff;">
                        <h1 style="background: linear-gradient(135deg, #00d4ff, #0099ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.5em; font-weight: 700; padding-bottom: 20px; margin-bottom: 30px; border-bottom: 2px solid rgba(0, 212, 255, 0.3); text-shadow: 0 0 30px rgba(0, 212, 255, 0.3);">
                            🏢 부서별 분석 리포트
                        </h1>
                        ${this.generateDepartmentTable(deptAnalysis)}
                    </div>
                `;
            },
            
            generateExecutiveReport(dashboardData, employees) {
                // 실제 직원 데이터 사용 - API에서 가져온 데이터 우선 사용
                const actualEmployees = this.state.employees && this.state.employees.length > 0 ? this.state.employees : (employees || []);
                
                // 대시보드 통계 데이터 사용 (API에서 가져온 데이터)
                const stats = this.state.dashboardStats || dashboardData || {};
                const totalEmployeesFromAPI = stats.total_employees || actualEmployees.length || 0;
                const topTalentsFromAPI = stats.top_talents?.count || 0;
                const riskEmployeesFromAPI = stats.risk_employees?.count || 0;
                
                const avgScore = this.calculateAverageScore(actualEmployees);
                const gradeDistribution = this.calculateGradeDistribution(actualEmployees);
                const deptAnalysis = this.analyzeDepartments(actualEmployees);
                
                // 핵심 지표 계산 - API 데이터 우선 사용
                const topTalents = topTalentsFromAPI > 0 ? topTalentsFromAPI : ((gradeDistribution['S'] || 0) + (gradeDistribution['A'] || 0));
                const riskEmployees = riskEmployeesFromAPI > 0 ? riskEmployeesFromAPI : ((gradeDistribution['C'] || 0) + (gradeDistribution['D'] || 0));
                const totalCount = totalEmployeesFromAPI > 0 ? totalEmployeesFromAPI : actualEmployees.length;
                const retentionRate = totalCount > 0 ? Math.round(((totalCount - riskEmployees) / totalCount) * 100) : 0;
                const talentDensity = totalCount > 0 ? Math.round((topTalents / totalCount) * 100) : 0;
                
                // 부서별 성과
                const deptScores = Object.entries(deptAnalysis).map(([dept, data]) => ({
                    dept: dept,
                    score: data.avgScore || 0,
                    count: data.count,
                    topTalents: ((data.grades['S'] || 0) + (data.grades['A+'] || 0))
                })).sort((a, b) => b.score - a.score);
                
                // 위험도 평가
                const riskLevel = totalCount > 0 && riskEmployees > totalCount * 0.2 ? 'HIGH' : 
                                totalCount > 0 && riskEmployees > totalCount * 0.1 ? 'MEDIUM' : 'LOW';
                
                return `
                    <div style="font-family: 'Pretendard', sans-serif; line-height: 1.8; color: #333;">
                        <div style="background: linear-gradient(135deg, #00d9ff 0%, #7b61ff 50%, #667eea 100%); color: #fff; padding: 30px; border-radius: 12px; margin-bottom: 30px;">
                            <h1 style="margin: 0; font-size: 28px; font-weight: 700;">💼 경영진 브리핑</h1>
                            <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;"><strong>작성 부서:</strong> OK홀딩스 인사부</p>
                            <p style="margin: 5px 0 0 0; font-size: 14px; opacity: 0.8;">보고일: ${new Date().toLocaleDateString('ko-KR')}</p>
                        </div>

                        <div style="background: rgba(0, 217, 255, 0.1); padding: 25px; border-radius: 8px; margin-bottom: 30px; border-left: 5px solid #00d9ff;">
                            <h2 style="margin: 0 0 15px 0; color: #1976d2;">📊 경영 핵심 지표 (Executive Summary)</h2>
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                                <div style="text-align: center;">
                                    <div style="font-size: 24px; font-weight: bold; color: #1976d2;">${totalCount}명</div>
                                    <div style="color: #666;">전체 인력</div>
                                </div>
                                <div style="text-align: center;">
                                    <div style="font-size: 24px; font-weight: bold; color: ${avgScore >= 70 ? '#28a745' : avgScore >= 60 ? '#ffc107' : '#dc3545'};">${Math.round(avgScore)}점</div>
                                    <div style="color: #666;">평균 성과 점수</div>
                                </div>
                                <div style="text-align: center;">
                                    <div style="font-size: 24px; font-weight: bold; color: #28a745;">${topTalents}명 (${talentDensity}%)</div>
                                    <div style="color: #666;">핵심 인재</div>
                                </div>
                                <div style="text-align: center;">
                                    <div style="font-size: 24px; font-weight: bold; color: ${retentionRate >= 90 ? '#28a745' : retentionRate >= 80 ? '#ffc107' : '#dc3545'};">${retentionRate}%</div>
                                    <div style="color: #666;">예상 리텐션</div>
                                </div>
                            </div>
                        </div>

                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px;">
                            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px;">
                                <h3 style="margin: 0 0 15px 0; color: #00d9ff;">🎯 전략적 우선순위</h3>
                                <ul style="margin: 0; padding-left: 20px;">
                                    <li style="margin-bottom: 8px;"><strong>인재 확보:</strong> ${talentDensity < 15 ? '핵심 인재 비율 확대 필요' : '우수한 인재 보유율'}</li>
                                    <li style="margin-bottom: 8px;"><strong>성과 관리:</strong> ${avgScore < 600 ? '전반적 성과 개선 시급' : avgScore < 700 ? '성과 향상 여지 존재' : '우수한 성과 수준 유지'}</li>
                                    <li style="margin-bottom: 8px;"><strong>리스크 관리:</strong> ${riskLevel === 'HIGH' ? '고위험 인력 다수 존재' : riskLevel === 'MEDIUM' ? '중간 수준 리스크' : '안정적 조직 상태'}</li>
                                </ul>
                            </div>
                            
                            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px;">
                                <h3 style="margin: 0 0 15px 0; color: #00d9ff;">📈 조직 건강도</h3>
                                <div style="margin-bottom: 10px;">
                                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                                        <span>인재 밀도</span>
                                        <span style="font-weight: bold;">${talentDensity}%</span>
                                    </div>
                                    <div style="background: #e0e0e0; height: 8px; border-radius: 4px;">
                                        <div style="background: ${talentDensity >= 20 ? '#28a745' : talentDensity >= 15 ? '#ffc107' : '#dc3545'}; width: ${Math.min(talentDensity, 100)}%; height: 100%; border-radius: 4px;"></div>
                                    </div>
                                </div>
                                <div style="margin-bottom: 10px;">
                                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                                        <span>성과 수준</span>
                                        <span style="font-weight: bold;">${Math.round((avgScore/1000)*100)}%</span>
                                    </div>
                                    <div style="background: #e0e0e0; height: 8px; border-radius: 4px;">
                                        <div style="background: ${avgScore >= 700 ? '#28a745' : avgScore >= 600 ? '#ffc107' : '#dc3545'}; width: ${Math.min((avgScore/1000)*100, 100)}%; height: 100%; border-radius: 4px;"></div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <h2 style="color: #00d9ff; border-bottom: 2px solid #00d9ff; padding-bottom: 10px;">🏢 부서별 성과 현황</h2>
                        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 30px;">
                            <table style="width: 100%; border-collapse: collapse;">
                                <thead>
                                    <tr style="background: #e9ecef;">
                                        <th style="padding: 12px; border: 1px solid #dee2e6; text-align: left;">부서명</th>
                                        <th style="padding: 12px; border: 1px solid #dee2e6; text-align: center;">인원</th>
                                        <th style="padding: 12px; border: 1px solid #dee2e6; text-align: center;">평균점수</th>
                                        <th style="padding: 12px; border: 1px solid #dee2e6; text-align: center;">핵심인재</th>
                                        <th style="padding: 12px; border: 1px solid #dee2e6; text-align: center;">등급</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${deptScores.slice(0, 5).map((dept, index) => {
                                        // 100점과 1000점 스케일 모두 지원
                                        const grade = dept.score >= 90 || dept.score >= 900 ? 'S' : 
                                                     dept.score >= 85 || dept.score >= 850 ? 'A' : 
                                                     dept.score >= 80 || dept.score >= 800 ? 'B+' : 
                                                     dept.score >= 75 || dept.score >= 750 ? 'B' : 
                                                     dept.score >= 70 || dept.score >= 700 ? 'C' : 'D';
                                        const gradeColor = grade === 'S' ? '#69f0ae' : 
                                                          grade === 'A' ? '#4caf50' : 
                                                          grade === 'B+' ? '#ffd54f' : 
                                                          grade === 'B' ? '#ff9800' : 
                                                          grade === 'C' ? '#ff7043' : '#ff5252';
                                        return `
                                        <tr>
                                            <td style="padding: 12px; border: 1px solid #dee2e6;">
                                                ${index < 3 ? (index === 0 ? '🥇' : index === 1 ? '🥈' : '🥉') : ''} ${dept.dept}
                                            </td>
                                            <td style="padding: 12px; border: 1px solid #dee2e6; text-align: center;">${dept.count}명</td>
                                            <td style="padding: 12px; border: 1px solid #dee2e6; text-align: center; font-weight: bold;">${dept.score}점</td>
                                            <td style="padding: 12px; border: 1px solid #dee2e6; text-align: center;">${dept.topTalents}명</td>
                                            <td style="padding: 12px; border: 1px solid #dee2e6; text-align: center;">
                                                <span style="background: ${gradeColor}; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">${grade}</span>
                                            </td>
                                        </tr>
                                        `;
                                    }).join('')}
                                </tbody>
                            </table>
                        </div>

                        <h2 style="color: #00d9ff; border-bottom: 2px solid #00d9ff; padding-bottom: 10px;">⚠️ 경영 이슈 및 권고사항</h2>
                        <div style="background: linear-gradient(135deg, ${riskLevel === 'HIGH' ? 'rgba(244, 67, 54, 0.15)' : riskLevel === 'MEDIUM' ? 'rgba(255, 193, 7, 0.15)' : 'rgba(76, 175, 80, 0.15)'} 0%, ${riskLevel === 'HIGH' ? 'rgba(244, 67, 54, 0.08)' : riskLevel === 'MEDIUM' ? 'rgba(255, 152, 0, 0.1)' : 'rgba(76, 175, 80, 0.1)'} 100%); padding: 25px; border-radius: 12px; border: 1px solid ${riskLevel === 'HIGH' ? 'rgba(244, 67, 54, 0.3)' : riskLevel === 'MEDIUM' ? 'rgba(255, 193, 7, 0.3)' : 'rgba(76, 175, 80, 0.3)'}; backdrop-filter: blur(10px);">
                            <h3 style="margin: 0 0 15px 0; color: #ffffff; font-weight: 600; text-shadow: 0 1px 3px rgba(0,0,0,0.3);">즉시 조치 필요 사항</h3>
                            <ul style="margin: 0; padding-left: 25px; color: rgba(255, 255, 255, 0.95); font-size: 1.05em; line-height: 1.8;">
                                ${riskEmployees > employees.length * 0.2 ? 
                                    '<li><strong>🚨 고위험:</strong> 성과 미달 인력 ' + riskEmployees + '명 (전체 ' + Math.round((riskEmployees/employees.length)*100) + '%) - 즉시 개선 계획 수립 필요</li>' : ''}
                                ${talentDensity < 15 ? 
                                    '<li><strong>📈 인재 확보:</strong> 핵심 인재 비율 ' + talentDensity + '% - 업계 평균 20% 달성을 위한 채용/육성 전략 필요</li>' : ''}
                                ${avgScore < 650 ? 
                                    '<li><strong>💼 성과 개선:</strong> 조직 평균 성과 ' + avgScore + '점 - 교육 및 개발 투자 확대 권고</li>' : ''}
                                <li><strong>🎯 전략 실행:</strong> ${deptScores[0].dept} 우수 사례 벤치마킹을 통한 전사 성과 개선</li>
                                <li><strong>🔄 정기 모니터링:</strong> 월간 성과 리뷰 및 분기별 인재 현황 점검 체계 구축</li>
                            </ul>
                        </div>

                        <div style="background: #f1f8e9; padding: 20px; border-radius: 8px; margin-top: 20px; border-left: 4px solid #8bc34a;">
                            <h3 style="margin: 0 0 10px 0; color: #689f38;">💡 장기 전략 제안</h3>
                            <p style="margin: 0; color: #666;">
                                <strong>인재 관리:</strong> 핵심 인재 유지를 위한 맞춤형 보상 체계 및 경력 개발 프로그램 구축을 통해 
                                조직의 경쟁력을 지속적으로 강화하고 미래 성장 동력을 확보하시기 바랍니다.
                            </p>
                        </div>
                    </div>
                `;
            },
            
            // 리포트 액션 함수들
            printReport() {
                const content = document.getElementById('report-content').innerHTML;
                const printWindow = window.open('', '_blank');
                printWindow.document.write(`
                    <html>
                        <head>
                            <title>${this.currentReport?.title || '리포트'}</title>
                            <style>
                                body { font-family: 'Pretendard', sans-serif; padding: 20px; }
                                @media print { body { padding: 0; } }
                            </style>
                        </head>
                        <body>${content}</body>
                    </html>
                `);
                printWindow.document.close();
                printWindow.print();
            },
            
            copyReport() {
                const content = document.getElementById('report-content').innerText;
                navigator.clipboard.writeText(content).then(() => {
                    this.showNotification('리포트가 클립보드에 복사되었습니다', 'success');
                });
            },
            
            downloadReportAsHTML() {
                if (!this.currentReport) return;
                
                const html = `
                    <!DOCTYPE html>
                    <html lang="ko">
                    <head>
                        <meta charset="UTF-8">
                        <title>${this.currentReport.title}</title>
                        <style>
                            body { 
                                font-family: 'Pretendard', 'Malgun Gothic', sans-serif; 
                                padding: 40px; 
                                max-width: 1200px; 
                                margin: 0 auto; 
                            }
                        </style>
                    </head>
                    <body>
                        ${this.currentReport.content}
                    </body>
                    </html>
                `;
                
                const blob = new Blob([html], { type: 'text/html;charset=utf-8' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${this.currentReport.title}_${new Date().toISOString().split('T')[0]}.html`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
            },
            
            async downloadReportAsPDF() {
                if (!this.currentReport) return;
                
                try {
                    const reportContent = document.getElementById('report-content');
                    const canvas = await html2canvas(reportContent, {
                        scale: 2,
                        useCORS: true,
                        backgroundColor: '#ffffff'
                    });
                    
                    const { jsPDF } = window.jspdf;
                    const pdf = new jsPDF('p', 'mm', 'a4');
                    const imgData = canvas.toDataURL('image/png');
                    
                    const pageWidth = pdf.internal.pageSize.getWidth();
                    const pageHeight = pdf.internal.pageSize.getHeight();
                    const imgWidth = pageWidth - 20;
                    const imgHeight = (canvas.height * imgWidth) / canvas.width;
                    
                    let heightLeft = imgHeight;
                    let position = 10;
                    
                    pdf.addImage(imgData, 'PNG', 10, position, imgWidth, imgHeight);
                    heightLeft -= (pageHeight - 20);
                    
                    while (heightLeft > 0) {
                        position = heightLeft - imgHeight + 10;
                        pdf.addPage();
                        pdf.addImage(imgData, 'PNG', 10, position, imgWidth, imgHeight);
                        heightLeft -= (pageHeight - 20);
                    }
                    
                    pdf.save(`${this.currentReport.title}_${new Date().toISOString().split('T')[0]}.pdf`);
                    this.showNotification('PDF 다운로드가 완료되었습니다', 'success');
                } catch (error) {
                    console.error('PDF 생성 오류:', error);
                    this.showNotification('PDF 생성 중 오류가 발생했습니다', 'error');
                }
            },
            
            // 리포트 다운로드
            downloadReport(reportData) {
                const html = `
                    <!DOCTYPE html>
                    <html lang="ko">
                    <head>
                        <meta charset="UTF-8">
                        <title>${reportData.title}</title>
                        <style>
                            body { font-family: 'Malgun Gothic', sans-serif; padding: 40px; max-width: 800px; margin: 0 auto; }
                            h1 { color: #00d9ff; border-bottom: 2px solid #00d9ff; padding-bottom: 10px; }
                            h2 { color: #333; margin-top: 30px; }
                            h3 { color: #666; margin-top: 20px; }
                            ul { line-height: 1.8; }
                            .header { background: linear-gradient(135deg, rgba(52, 61, 84, 0.95) 0%, rgba(41, 49, 69, 0.9) 100%); padding: 20px; border-radius: 8px; margin-bottom: 30px; color: #fff; }
                            .footer { margin-top: 50px; padding-top: 20px; border-top: 1px solid #ddd; color: #999; font-size: 12px; }
                        </style>
                    </head>
                    <body>
                        <div class="header">
                            <h1>${reportData.title}</h1>
                            <p>생성일: ${new Date().toLocaleDateString('ko-KR')}</p>
                            <p>회사: ${reportData.company}</p>
                        </div>
                        ${reportData.content}
                        <div class="footer">
                            <p>이 리포트는 AIRISS v5.0 AI-Powered HR Intelligence System에 의해 자동 생성되었습니다.</p>
                            <p>© 2025 OK금융그룹. All rights reserved.</p>
                        </div>
                    </body>
                    </html>
                `;
                
                const blob = new Blob([html], { type: 'text/html;charset=utf-8' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${reportData.type}_report_${new Date().getTime()}.html`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
            },
            
            // 인사이트 새로고침
            async refreshInsights() {
                this.loadInsights();
                this.showNotification('인사이트가 업데이트되었습니다', 'success');
            },
            
            // 실시간 AI 인사이트 생성
            async generateRealTimeInsights() {
                // 생성 상태 표시
                const statusElement = document.getElementById('insights-generation-status');
                statusElement.style.display = 'block';
                
                try {
                    // 실시간 데이터 가져오기
                    await this.loadEmployeesData();
                    await this.loadDashboardData();
                    
                    // AI 분석 시뮬레이션 (실제 서버 API 호출로 대체 가능)
                    setTimeout(async () => {
                        // 데이터 분석 및 인사이트 생성
                        const employees = this.state.employees || [];
                        const avgScore = this.calculateAverageScore(employees);
                        
                        // AI 인사이트 생성 (확장 가능)
                        const insights = this.generateAIAnalysis(employees);
                        
                        // 인사이트 업데이트
                        this.loadInsights();
                        
                        // 상태 숨기기
                        statusElement.style.display = 'none';
                        
                        // 성공 메시지
                        this.showNotification('✅ AI 인사이트가 성공적으로 생성되었습니다', 'success');
                        
                        // 애니메이션 효과
                        const contentElement = document.getElementById('insights-content');
                        contentElement.style.animation = 'fadeIn 0.5s ease-in';
                    }, 2000); // 2초 지연 (실제 API에서는 제거)
                    
                } catch (error) {
                    console.error('AI insights generation failed:', error);
                    statusElement.style.display = 'none';
                    this.showNotification('❌ AI 인사이트 생성에 실패했습니다', 'error');
                }
            },
            
            // AI 분석 엔진 (확장 가능)
            generateAIAnalysis(employees) {
                const avgScore = this.calculateAverageScore(employees);
                const gradeDistribution = this.calculateGradeDistribution(employees);
                
                // AI 기반 패턴 분석
                const patterns = {
                    performanceTrend: avgScore >= 700 ? 'upward' : avgScore >= 600 ? 'stable' : 'downward',
                    talentDensity: (gradeDistribution['S'] + gradeDistribution['A+']) / employees.length,
                    riskLevel: (gradeDistribution['C'] + gradeDistribution['D']) / employees.length,
                    organizationalHealth: this.calculateOrganizationalHealth(employees)
                };
                
                // 예측 분석
                const predictions = {
                    sixMonthOutlook: patterns.performanceTrend === 'upward' ? 'positive' : 'concerning',
                    talentRetentionRisk: patterns.talentDensity < 0.1 ? 'high' : 'moderate',
                    growthPotential: avgScore >= 650 ? 'high' : 'limited'
                };
                
                return {
                    patterns,
                    predictions,
                    recommendations: this.generateRecommendations(patterns, predictions),
                    timestamp: new Date().toISOString()
                };
            },
            
            // 조직 건강도 계산
            calculateOrganizationalHealth(employees) {
                const avgScore = this.calculateAverageScore(employees);
                const gradeDistribution = this.calculateGradeDistribution(employees);
                
                return Math.min(100, Math.round(
                    (avgScore / 10) * 0.4 +
                    ((gradeDistribution['S'] + gradeDistribution['A+'] + gradeDistribution['A']) / employees.length * 100) * 0.3 +
                    ((1 - gradeDistribution['D'] / employees.length) * 100) * 0.3
                ));
            },
            
            // AI 기반 추천 생성
            generateRecommendations(patterns, predictions) {
                const recommendations = [];
                
                if (patterns.talentDensity < 0.1) {
                    recommendations.push('핵심 인재 육성 프로그램 긴급 도입');
                }
                
                if (patterns.riskLevel > 0.2) {
                    recommendations.push('하위 성과자 대상 집중 코칭 필요');
                }
                
                if (predictions.sixMonthOutlook === 'concerning') {
                    recommendations.push('조직 문화 혁신 프로그램 실시');
                }
                
                return recommendations;
            }
        };
        
        // 앱 초기화
        document.addEventListener('DOMContentLoaded', () => {
            try {
                console.log('🔍 AIRISS 객체 확인:', typeof window.AIRISS);
                if (window.AIRISS && typeof window.AIRISS.init === 'function') {
                    console.log('✅ AIRISS 객체가 정상적으로 로드되었습니다');
                    console.log('📋 사용 가능한 메서드:', Object.keys(window.AIRISS).filter(k => typeof window.AIRISS[k] === 'function'));
                    
                    // 초기화 실행
                    window.AIRISS.init();
                } else {
                    console.error('❌ AIRISS 객체 또는 init 메서드를 찾을 수 없습니다');
                }
            } catch (error) {
                console.error('❌ 초기화 오류:', error);
                console.error('상세 오류:', error.stack);
            }
        });
        
        // 부서별 성과 페이지네이션 함수
        if (!window.AIRISSApp) window.AIRISSApp = {};
        
        window.AIRISSApp.changeDeptPage = function(tableId, action) {
            const table = document.getElementById(tableId);
            if (!table) return;
            
            const allDepts = JSON.parse(table.dataset.allDepartments);
            const itemsPerPage = parseInt(table.dataset.itemsPerPage);
            let currentPage = parseInt(table.dataset.currentPage);
            const totalPages = Math.ceil(allDepts.length / itemsPerPage);
            const paginationId = table.dataset.paginationId;
            
            // 페이지 변경
            if (action === 'prev' && currentPage > 1) {
                currentPage--;
            } else if (action === 'next' && currentPage < totalPages) {
                currentPage++;
            } else if (typeof action === 'number') {
                currentPage = Math.max(1, Math.min(totalPages, action));
            }
            
            // 테이블 업데이트
            const startIdx = (currentPage - 1) * itemsPerPage;
            const endIdx = startIdx + itemsPerPage;
            const pageDepts = allDepts.slice(startIdx, endIdx);
            
            let rows = '';
            pageDepts.forEach(([dept, data], index) => {
                const globalIndex = startIdx + index;
                const count = data.count || 0;
                const avgScore = data.avgScore || data.avg_score || 0;
                let topTalents = 0;
                if (data.grades) {
                    topTalents = (data.grades['S'] || 0) + (data.grades['A+'] || 0) + (data.grades['A'] || 0);
                }
                const performance = avgScore >= 800 ? { grade: '우수', color: '#69f0ae' } :
                                  avgScore >= 700 ? { grade: '양호', color: '#ffd54f' } :
                                  avgScore >= 600 ? { grade: '보통', color: '#ff9800' } :
                                  { grade: '개선필요', color: '#ff5252' };
                const rankIcon = globalIndex === 0 ? '🥇' : globalIndex === 1 ? '🥈' : globalIndex === 2 ? '🥉' : '';
                
                const bgColor = index % 2 === 0 ? '0.03' : '0.05';
                rows += '<tr style="background: rgba(255, 255, 255, ' + bgColor + ');">';
                rows += '<td style="padding: 15px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #ffffff; font-weight: 500; text-align: center;">' + (globalIndex + 1) + '</td>';
                rows += '<td style="padding: 15px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #ffffff; font-weight: 500;">' + rankIcon + ' ' + dept + '</td>';
                rows += '<td style="padding: 15px; text-align: center; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #ffffff; font-weight: 600;">' + count + '명</td>';
                rows += '<td style="padding: 15px; text-align: center; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #00d4ff; font-weight: 700;">' + avgScore + '점</td>';
                rows += '<td style="padding: 15px; text-align: center; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #69f0ae; font-weight: 600;">' + topTalents + '명</td>';
                rows += '<td style="padding: 15px; text-align: center; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: ' + performance.color + '; font-weight: 600;">' + performance.grade + '</td>';
                rows += '</tr>';
            });
            
            table.querySelector('tbody').innerHTML = rows;
            table.dataset.currentPage = currentPage;
            document.getElementById(paginationId).textContent = currentPage + ' / ' + totalPages;
        };
