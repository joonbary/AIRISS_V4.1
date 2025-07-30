/**
 * PDF 전용 레이아웃 컴포넌트
 * 화면에서는 hidden 상태로 유지되며, PDF 캡처 시에만 사용됨
 */
import React from 'react';
import { Radar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js';

// Chart.js 등록
ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

interface CompetencyScores {
  실행력: number;
  성장지향: number;
  협업: number;
  고객지향: number;
  전문성: number;
  혁신성: number;
  리더십: number;
  커뮤니케이션: number;
}

interface EmployeeData {
  employee_id: string;
  name: string;
  department: string;
  position: string;
  ai_score: number;
  grade: string;
  competencies: CompetencyScores;
  strengths: string[];
  improvements: string[];
  ai_comment: string;
  career_recommendation: string[];
  education_suggestion: string[];
  analyzed_at: string;
  confidence_score?: number;
  percentile_rank?: number;
}

interface EmployeePdfLayoutProps {
  employee: EmployeeData;
}

const EmployeePdfLayout: React.FC<EmployeePdfLayoutProps> = ({ employee }) => {
  // 등급별 색상
  const getGradeColor = (grade: string) => {
    switch (grade) {
      case 'S': return '#9c27b0';
      case 'A+': return '#2196f3';
      case 'A': return '#03a9f4';
      case 'B': return '#4caf50';
      case 'C': return '#ff9800';
      case 'D': return '#f44336';
      default: return '#757575';
    }
  };

  // 레이더 차트 데이터
  const radarData = {
    labels: Object.keys(employee.competencies),
    datasets: [{
      label: employee.name,
      data: Object.values(employee.competencies),
      backgroundColor: 'rgba(33, 150, 243, 0.2)',
      borderColor: 'rgba(33, 150, 243, 1)',
      borderWidth: 2,
      pointBackgroundColor: 'rgba(33, 150, 243, 1)',
      pointBorderColor: '#fff',
      pointHoverBackgroundColor: '#fff',
      pointHoverBorderColor: 'rgba(33, 150, 243, 1)',
    }],
  };

  const radarOptions = {
    scales: {
      r: {
        beginAtZero: true,
        max: 100,
        ticks: {
          stepSize: 20,
          font: {
            size: 10,
          },
        },
        grid: {
          color: '#e0e0e0',
        },
      },
    },
    plugins: {
      legend: {
        display: false,
      },
    },
    maintainAspectRatio: true,
    responsive: false,
  };

  // PDF 전용 스타일 (픽셀 단위 고정)
  const styles = {
    container: {
      width: '794px',
      height: '1123px',
      backgroundColor: '#ffffff',
      padding: '40px',
      boxSizing: 'border-box' as const,
      fontFamily: 'Malgun Gothic, Apple SD Gothic Neo, sans-serif',
      fontSize: '14px',
      lineHeight: '1.6',
      color: '#333333',
      position: 'absolute' as const,
      left: '-9999px',
      top: '0',
    },
    header: {
      marginBottom: '30px',
      borderBottom: '3px solid #1976d2',
      paddingBottom: '20px',
    },
    logo: {
      display: 'flex',
      alignItems: 'center',
      marginBottom: '15px',
    },
    logoText: {
      fontSize: '24px',
      fontWeight: 'bold' as const,
      color: '#1976d2',
      marginRight: '10px',
    },
    logoVersion: {
      fontSize: '14px',
      color: '#666666',
    },
    title: {
      fontSize: '28px',
      fontWeight: 'bold' as const,
      color: '#1976d2',
      marginBottom: '10px',
    },
    subtitle: {
      fontSize: '16px',
      color: '#666666',
    },
    section: {
      marginBottom: '25px',
    },
    sectionTitle: {
      fontSize: '18px',
      fontWeight: 'bold' as const,
      color: '#2c3e50',
      marginBottom: '12px',
      borderBottom: '2px solid #e0e0e0',
      paddingBottom: '5px',
    },
    infoGrid: {
      display: 'grid',
      gridTemplateColumns: '1fr 1fr',
      gap: '20px',
      marginBottom: '20px',
    },
    infoCard: {
      backgroundColor: '#f5f5f5',
      padding: '15px',
      borderRadius: '8px',
      border: '1px solid #e0e0e0',
    },
    infoLabel: {
      fontSize: '12px',
      color: '#666666',
      marginBottom: '5px',
    },
    infoValue: {
      fontSize: '16px',
      fontWeight: 'bold' as const,
      color: '#333333',
    },
    scoreCard: {
      backgroundColor: '#e3f2fd',
      padding: '20px',
      borderRadius: '8px',
      textAlign: 'center' as const,
      marginBottom: '20px',
    },
    scoreValue: {
      fontSize: '48px',
      fontWeight: 'bold' as const,
      color: '#1976d2',
    },
    gradeChip: {
      display: 'inline-block',
      padding: '5px 15px',
      borderRadius: '20px',
      color: '#ffffff',
      fontWeight: 'bold' as const,
      fontSize: '16px',
      marginLeft: '10px',
    },
    chartContainer: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'flex-start',
      marginBottom: '20px',
    },
    radarChart: {
      width: '350px',
      height: '350px',
    },
    competencyList: {
      flex: 1,
      marginLeft: '30px',
    },
    competencyItem: {
      display: 'flex',
      justifyContent: 'space-between',
      padding: '8px 0',
      borderBottom: '1px solid #e0e0e0',
    },
    strengthsList: {
      display: 'flex',
      flexWrap: 'wrap' as const,
      gap: '10px',
      marginBottom: '15px',
    },
    strengthChip: {
      backgroundColor: '#4caf50',
      color: '#ffffff',
      padding: '5px 12px',
      borderRadius: '16px',
      fontSize: '13px',
    },
    improvementChip: {
      backgroundColor: '#ff9800',
      color: '#ffffff',
      padding: '5px 12px',
      borderRadius: '16px',
      fontSize: '13px',
    },
    feedbackBox: {
      backgroundColor: '#f5f5f5',
      padding: '15px',
      borderRadius: '8px',
      border: '1px solid #e0e0e0',
      marginBottom: '15px',
    },
    footer: {
      position: 'absolute' as const,
      bottom: '30px',
      left: '40px',
      right: '40px',
      borderTop: '1px solid #e0e0e0',
      paddingTop: '15px',
      fontSize: '12px',
      color: '#666666',
      textAlign: 'center' as const,
    },
  };

  return (
    <div id={`employee-pdf-layout-${employee.employee_id}`} style={styles.container}>
      {/* 헤더 */}
      <div style={styles.header}>
        <div style={styles.logo}>
          <span style={styles.logoText}>AIRISS</span>
          <span style={styles.logoVersion}>v4.0</span>
        </div>
        <h1 style={styles.title}>AI 인재 분석 리포트</h1>
        <div style={styles.subtitle}>
          {employee.name} | {employee.department} {employee.position}
        </div>
      </div>

      {/* 기본 정보 */}
      <div style={styles.section}>
        <div style={styles.infoGrid}>
          <div style={styles.infoCard}>
            <div style={styles.infoLabel}>사번</div>
            <div style={styles.infoValue}>{employee.employee_id}</div>
          </div>
          <div style={styles.infoCard}>
            <div style={styles.infoLabel}>분석일시</div>
            <div style={styles.infoValue}>
              {new Date(employee.analyzed_at).toLocaleDateString('ko-KR')}
            </div>
          </div>
        </div>
      </div>

      {/* AI 종합 평가 */}
      <div style={styles.section}>
        <h2 style={styles.sectionTitle}>AI 종합 평가</h2>
        <div style={styles.scoreCard}>
          <span style={styles.scoreValue}>{employee.ai_score}</span>
          <span style={{...styles.gradeChip, backgroundColor: getGradeColor(employee.grade)}}>
            {employee.grade}등급
          </span>
        </div>
      </div>

      {/* 8대 핵심 역량 */}
      <div style={styles.section}>
        <h2 style={styles.sectionTitle}>8대 핵심 역량 분석</h2>
        <div style={styles.chartContainer}>
          <div style={styles.radarChart}>
            <Radar data={radarData} options={radarOptions} width={350} height={350} />
          </div>
          <div style={styles.competencyList}>
            {Object.entries(employee.competencies).map(([key, value]) => (
              <div key={key} style={styles.competencyItem}>
                <span>{key}</span>
                <span style={{ fontWeight: 'bold', color: value >= 80 ? '#4caf50' : '#333333' }}>
                  {value}점
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 강점 및 개선점 */}
      <div style={styles.section}>
        <h2 style={styles.sectionTitle}>강점 분석</h2>
        <div style={styles.strengthsList}>
          {employee.strengths.map((strength, index) => (
            <span key={index} style={styles.strengthChip}>{strength}</span>
          ))}
        </div>
      </div>

      <div style={styles.section}>
        <h2 style={styles.sectionTitle}>개발 필요 영역</h2>
        <div style={styles.strengthsList}>
          {employee.improvements.map((improvement, index) => (
            <span key={index} style={styles.improvementChip}>{improvement}</span>
          ))}
        </div>
      </div>

      {/* AI 종합 피드백 */}
      <div style={styles.section}>
        <h2 style={styles.sectionTitle}>AI 종합 피드백</h2>
        <div style={styles.feedbackBox}>
          {employee.ai_comment}
        </div>
      </div>

      {/* Footer */}
      <div style={styles.footer}>
        본 리포트는 AIRISS v4.0 AI 시스템에 의해 생성되었습니다. | 
        AI 신뢰도: {employee.confidence_score || 92}% | 
        © 2024 AIRISS. All rights reserved.
      </div>
    </div>
  );
};

export default EmployeePdfLayout;