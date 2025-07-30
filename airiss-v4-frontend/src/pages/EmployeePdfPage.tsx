/**
 * 직원 상세 리포트 PDF 출력 전용 페이지
 * A4 규격(794px × 1123px)에 최적화된 레이아웃
 */
import React, { useEffect, useState } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';
import { employeeApi } from '../services/employeeApi';

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
  uid?: string;
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

const EmployeePdfPage: React.FC = () => {
  const { uid } = useParams<{ uid: string }>();
  const [searchParams] = useSearchParams();
  const [employee, setEmployee] = useState<EmployeeData | null>(null);
  const [loading, setLoading] = useState(true);

  // 직원 데이터 로드
  useEffect(() => {
    const loadEmployeeData = async () => {
      if (!uid) return;
      
      try {
        const data = await employeeApi.getEmployeeDetail(uid);
        setEmployee(data);
      } catch (error) {
        console.error('직원 데이터 로드 실패:', error);
      } finally {
        setLoading(false);
      }
    };

    loadEmployeeData();
  }, [uid]);

  // 레이더 차트 그리기 (Canvas 직접 사용)
  const drawRadarChart = (canvasId: string, employeeData: EmployeeData) => {
    const canvas = document.getElementById(canvasId) as HTMLCanvasElement;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const centerX = 150;
    const centerY = 150;
    const radius = 100;
    const competencies = Object.entries(employeeData.competencies);
    const angleStep = (2 * Math.PI) / competencies.length;

    // 배경 그리드
    ctx.strokeStyle = '#e0e0e0';
    ctx.lineWidth = 1;
    
    // 동심원 그리기
    for (let i = 1; i <= 5; i++) {
      ctx.beginPath();
      const r = (radius / 5) * i;
      ctx.arc(centerX, centerY, r, 0, 2 * Math.PI);
      ctx.stroke();
    }

    // 축 그리기
    competencies.forEach((_, index) => {
      const angle = angleStep * index - Math.PI / 2;
      const x = centerX + radius * Math.cos(angle);
      const y = centerY + radius * Math.sin(angle);
      
      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.lineTo(x, y);
      ctx.stroke();
    });

    // 데이터 그리기
    ctx.fillStyle = 'rgba(33, 150, 243, 0.3)';
    ctx.strokeStyle = '#2196f3';
    ctx.lineWidth = 2;
    
    ctx.beginPath();
    competencies.forEach(([, score], index) => {
      const angle = angleStep * index - Math.PI / 2;
      const r = (radius * score) / 100;
      const x = centerX + r * Math.cos(angle);
      const y = centerY + r * Math.sin(angle);
      
      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    // 라벨 그리기
    ctx.fillStyle = '#333333';
    ctx.font = '12px Malgun Gothic';
    ctx.textAlign = 'center';
    
    competencies.forEach(([name, score], index) => {
      const angle = angleStep * index - Math.PI / 2;
      const labelRadius = radius + 20;
      const x = centerX + labelRadius * Math.cos(angle);
      const y = centerY + labelRadius * Math.sin(angle);
      
      ctx.fillText(name, x, y);
      ctx.fillText(`${score}`, x, y + 15);
    });
  };

  // Canvas 렌더링을 위한 useEffect
  useEffect(() => {
    if (employee) {
      setTimeout(() => {
        drawRadarChart('radar-chart', employee);
      }, 100);
    }
  }, [employee]);

  // 자동 다운로드 처리
  useEffect(() => {
    if (employee && searchParams.get('download') === 'true') {
      setTimeout(() => {
        generatePDF();
      }, 1500); // 렌더링 대기
    }
  }, [employee, searchParams]);

  const generatePDF = async () => {
    const element = document.getElementById('pdf-content');
    if (!element || !employee) return;

    try {
      const canvas = await html2canvas(element, {
        scale: 2,
        useCORS: true,
        logging: false,
        backgroundColor: '#ffffff',
        width: 794,
        height: 1123,
      });

      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF('p', 'mm', 'a4');
      
      // A4 전체에 이미지 삽입
      pdf.addImage(imgData, 'PNG', 0, 0, 210, 297);
      
      const fileName = `AI_리포트_${employee.name}_${employee.employee_id}_${new Date().toISOString().slice(0, 10)}.pdf`;
      pdf.save(fileName);
      
      // 다운로드 후 창 닫기
      setTimeout(() => {
        window.close();
      }, 1000);
    } catch (error) {
      console.error('PDF 생성 오류:', error);
      alert('PDF 생성 중 오류가 발생했습니다.');
    }
  };

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        fontFamily: 'Malgun Gothic, sans-serif'
      }}>
        <div>직원 데이터를 불러오는 중...</div>
      </div>
    );
  }

  if (!employee) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        fontFamily: 'Malgun Gothic, sans-serif'
      }}>
        <div>직원 데이터를 찾을 수 없습니다.</div>
      </div>
    );
  }

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

  // 역량 평가
  const getCompetencyEval = (score: number) => {
    if (score >= 90) return '탁월';
    if (score >= 80) return '우수';
    if (score >= 70) return '양호';
    if (score >= 60) return '보통';
    return '개선필요';
  };


  return (
    <div style={{ backgroundColor: '#f5f5f5', minHeight: '100vh', padding: '20px' }}>
      <div
        id="pdf-content"
        style={{
          width: '794px',
          height: '1123px',
          margin: '0 auto',
          backgroundColor: '#ffffff',
          padding: '40px',
          boxSizing: 'border-box',
          fontFamily: 'Malgun Gothic, Apple SD Gothic Neo, sans-serif',
          fontSize: '14px',
          lineHeight: '1.6',
          color: '#333333',
          position: 'relative',
        }}
      >
        {/* 헤더 */}
        <div style={{
          marginBottom: '25px',
          borderBottom: '3px solid #1976d2',
          paddingBottom: '15px',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#1976d2' }}>
                AIRISS <span style={{ fontSize: '14px', color: '#666' }}>v4.0</span>
              </div>
              <div style={{ fontSize: '20px', fontWeight: 'bold', marginTop: '5px' }}>
                AI 인재 분석 리포트
              </div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '16px', fontWeight: 'bold' }}>{employee.name}</div>
              <div style={{ fontSize: '14px', color: '#666' }}>
                {employee.department} | {employee.position}
              </div>
            </div>
          </div>
        </div>

        {/* 기본 정보 및 종합 점수 */}
        <div style={{ display: 'flex', gap: '20px', marginBottom: '20px' }}>
          <div style={{
            flex: 1,
            backgroundColor: '#f8f9fa',
            padding: '15px',
            borderRadius: '8px',
          }}>
            <div style={{ fontSize: '12px', color: '#666', marginBottom: '5px' }}>사번</div>
            <div style={{ fontSize: '16px', fontWeight: 'bold' }}>{employee.employee_id}</div>
          </div>
          <div style={{
            flex: 2,
            backgroundColor: '#e3f2fd',
            padding: '15px',
            borderRadius: '8px',
            textAlign: 'center',
          }}>
            <div style={{ fontSize: '12px', color: '#666', marginBottom: '5px' }}>AI 종합점수</div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px' }}>
              <span style={{ fontSize: '36px', fontWeight: 'bold', color: '#1976d2' }}>
                {employee.ai_score}
              </span>
              <span style={{
                padding: '5px 15px',
                borderRadius: '20px',
                backgroundColor: getGradeColor(employee.grade),
                color: '#ffffff',
                fontWeight: 'bold',
              }}>
                {employee.grade}등급
              </span>
            </div>
          </div>
          <div style={{
            flex: 1,
            backgroundColor: '#f8f9fa',
            padding: '15px',
            borderRadius: '8px',
          }}>
            <div style={{ fontSize: '12px', color: '#666', marginBottom: '5px' }}>백분위</div>
            <div style={{ fontSize: '16px', fontWeight: 'bold' }}>
              상위 {100 - (employee.percentile_rank || 75)}%
            </div>
          </div>
        </div>

        {/* 8대 핵심 역량 */}
        <div style={{ marginBottom: '20px' }}>
          <h3 style={{
            fontSize: '16px',
            fontWeight: 'bold',
            marginBottom: '10px',
            color: '#2c3e50',
          }}>
            8대 핵심 역량 분석
          </h3>
          <div style={{ display: 'flex', gap: '20px' }}>
            <div style={{ flex: 1 }}>
              <canvas
                id="radar-chart"
                width="300"
                height="300"
                style={{ maxWidth: '100%' }}
              />
            </div>
            <div style={{ flex: 1 }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid #e0e0e0' }}>
                    <th style={{ padding: '8px', textAlign: 'left', fontSize: '13px' }}>역량</th>
                    <th style={{ padding: '8px', textAlign: 'center', fontSize: '13px' }}>점수</th>
                    <th style={{ padding: '8px', textAlign: 'center', fontSize: '13px' }}>평가</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(employee.competencies).map(([name, score]) => (
                    <tr key={name} style={{ borderBottom: '1px solid #f0f0f0' }}>
                      <td style={{ padding: '6px', fontSize: '12px' }}>{name}</td>
                      <td style={{ padding: '6px', textAlign: 'center', fontWeight: 'bold' }}>
                        {score}
                      </td>
                      <td style={{ padding: '6px', textAlign: 'center', fontSize: '12px' }}>
                        {getCompetencyEval(score)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* 강점 및 개선점 */}
        <div style={{ display: 'flex', gap: '20px', marginBottom: '20px' }}>
          <div style={{ flex: 1 }}>
            <h3 style={{
              fontSize: '16px',
              fontWeight: 'bold',
              marginBottom: '10px',
              color: '#2c3e50',
            }}>
              핵심 강점
            </h3>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {employee.strengths.map((strength, index) => (
                <span
                  key={index}
                  style={{
                    padding: '4px 12px',
                    borderRadius: '16px',
                    backgroundColor: '#4caf50',
                    color: '#ffffff',
                    fontSize: '12px',
                  }}
                >
                  {strength}
                </span>
              ))}
            </div>
          </div>
          <div style={{ flex: 1 }}>
            <h3 style={{
              fontSize: '16px',
              fontWeight: 'bold',
              marginBottom: '10px',
              color: '#2c3e50',
            }}>
              개발 필요 영역
            </h3>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {employee.improvements.map((improvement, index) => (
                <span
                  key={index}
                  style={{
                    padding: '4px 12px',
                    borderRadius: '16px',
                    backgroundColor: '#ff9800',
                    color: '#ffffff',
                    fontSize: '12px',
                  }}
                >
                  {improvement}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* AI 종합 피드백 */}
        <div style={{ marginBottom: '20px' }}>
          <h3 style={{
            fontSize: '16px',
            fontWeight: 'bold',
            marginBottom: '10px',
            color: '#2c3e50',
          }}>
            AI 종합 피드백
          </h3>
          <div style={{
            backgroundColor: '#f8f9fa',
            padding: '15px',
            borderRadius: '8px',
            fontSize: '13px',
            lineHeight: '1.8',
          }}>
            {employee.ai_comment}
          </div>
        </div>

        {/* 경력 개발 추천 */}
        <div style={{ marginBottom: '20px' }}>
          <h3 style={{
            fontSize: '16px',
            fontWeight: 'bold',
            marginBottom: '10px',
            color: '#2c3e50',
          }}>
            추천 경력 개발 방향
          </h3>
          <ul style={{ margin: 0, paddingLeft: '20px' }}>
            {employee.career_recommendation.map((career, index) => (
              <li key={index} style={{ fontSize: '13px', marginBottom: '5px' }}>
                {career}
              </li>
            ))}
          </ul>
        </div>

        {/* Footer */}
        <div style={{
          position: 'absolute',
          bottom: '30px',
          left: '40px',
          right: '40px',
          borderTop: '1px solid #e0e0e0',
          paddingTop: '10px',
          fontSize: '11px',
          color: '#666666',
          textAlign: 'center',
        }}>
          본 리포트는 AIRISS v4.0 AI 시스템에 의해 생성되었습니다. | 
          분석일시: {new Date(employee.analyzed_at).toLocaleDateString('ko-KR')} | 
          AI 신뢰도: {employee.confidence_score || 92}%
        </div>
      </div>
    </div>
  );
};

export default EmployeePdfPage;