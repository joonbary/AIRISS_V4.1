// ===============================
// AIRISS v5.0 - Configuration
// ===============================
// Central configuration file for all settings
// ===============================

const AIRISS_CONFIG = {
    // API Configuration
    API: {
        BASE_URL: '/api',
        TIMEOUT: 30000,
        RETRY_ATTEMPTS: 3,
        RETRY_DELAY: 1000
    },
    
    // Chart Configuration
    CHARTS: {
        COLORS: {
            primary: '#00d4ff',
            secondary: '#667eea',
            success: '#10B981',
            warning: '#F59E0B',
            error: '#EF4444',
            info: '#3B82F6'
        },
        DEFAULT_OPTIONS: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 750
            }
        }
    },
    
    // Grade System Configuration
    GRADES: {
        THRESHOLDS: {
            S: { min: 90, label: 'S (최우수)', color: '#69f0ae' },
            A: { min: 85, label: 'A (우수)', color: '#4caf50' },
            B_PLUS: { min: 80, label: 'B+ (양호)', color: '#ffd54f' },
            B: { min: 75, label: 'B (평균)', color: '#ff9800' },
            C: { min: 70, label: 'C (미흡)', color: '#ff7043' },
            D: { min: 0, label: 'D (개선필요)', color: '#ff5252' }
        },
        // Support both 100-point and 1000-point scales
        AUTO_SCALE_DETECTION: true
    },
    
    // Department Configuration
    DEPARTMENTS: [
        '경영지원부',
        '영업부',
        'IT개발부',
        '마케팅부',
        '인사부',
        '재무부',
        '연구개발부',
        '고객서비스부',
        '전략기획부',
        '리스크관리부'
    ],
    
    // UI Configuration
    UI: {
        ANIMATION_DURATION: 300,
        DEBOUNCE_DELAY: 500,
        TOAST_DURATION: 3000,
        MODAL_BACKDROP_OPACITY: 0.6,
        SIDEBAR_WIDTH: 250,
        SIDEBAR_COLLAPSED_WIDTH: 20
    },
    
    // Storage Keys
    STORAGE: {
        SIDEBAR_STATE: 'sidebarCollapsed',
        USER_PREFERENCES: 'userPreferences',
        CACHE_PREFIX: 'airiss_cache_'
    },
    
    // Validation Rules
    VALIDATION: {
        MIN_SCORE: 0,
        MAX_SCORE: 100,
        MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
        ALLOWED_FILE_TYPES: ['.xlsx', '.xls', '.csv'],
        MIN_EMPLOYEES: 1,
        MAX_EMPLOYEES: 10000
    },
    
    // Feature Flags
    FEATURES: {
        ENABLE_AI_ANALYSIS: true,
        ENABLE_EXPORT: true,
        ENABLE_REAL_TIME_SYNC: true,
        ENABLE_DARK_MODE: true,
        ENABLE_NOTIFICATIONS: true
    },
    
    // Performance Configuration
    PERFORMANCE: {
        BATCH_SIZE: 100,
        LAZY_LOAD_THRESHOLD: 50,
        CACHE_DURATION: 5 * 60 * 1000, // 5 minutes
        MAX_CONCURRENT_REQUESTS: 5
    }
};

// Freeze configuration to prevent modifications
Object.freeze(AIRISS_CONFIG);

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AIRISS_CONFIG;
}