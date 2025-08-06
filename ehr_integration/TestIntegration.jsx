/**
 * Test Component for EHR-AIRISS Integration
 * 통합 테스트를 위한 독립 실행 가능한 컴포넌트
 */

import React, { useState } from 'react';
import EHRAirissIntegration from './EHR_AirissIntegration';
import './EHR_AirissIntegration.css';

// Sample employee data for testing
const SAMPLE_EMPLOYEES = [
  {
    id: "EMP001",
    name: "김철수",
    department: "개발팀",
    position: "선임개발자",
    goalAchievement: 92,
    projectSuccess: 88,
    customerSatisfaction: 95,
    attendance: 98,
    leadership: 85,
    technical: 90,
    communication: 82,
    problemSolving: 88,
    teamwork: 92,
    creativity: 78,
    adaptability: 85,
    reliability: 95
  },
  {
    id: "EMP002",
    name: "이영희",
    department: "마케팅팀",
    position: "과장",
    goalAchievement: 88,
    projectSuccess: 92,
    customerSatisfaction: 90,
    attendance: 96,
    leadership: 90,
    technical: 75,
    communication: 95,
    problemSolving: 85,
    teamwork: 88,
    creativity: 92,
    adaptability: 90,
    reliability: 88
  },
  {
    id: "EMP003",
    name: "박민수",
    department: "영업팀",
    position: "대리",
    goalAchievement: 85,
    projectSuccess: 87,
    customerSatisfaction: 92,
    attendance: 94,
    leadership: 78,
    technical: 70,
    communication: 90,
    problemSolving: 82,
    teamwork: 85,
    creativity: 75,
    adaptability: 88,
    reliability: 90
  },
  {
    id: "EMP004",
    name: "정수진",
    department: "인사팀",
    position: "팀장",
    goalAchievement: 95,
    projectSuccess: 93,
    customerSatisfaction: 88,
    attendance: 99,
    leadership: 95,
    technical: 82,
    communication: 92,
    problemSolving: 90,
    teamwork: 95,
    creativity: 85,
    adaptability: 92,
    reliability: 98
  },
  {
    id: "EMP005",
    name: "최동훈",
    department: "재무팀",
    position: "사원",
    goalAchievement: 82,
    projectSuccess: 85,
    customerSatisfaction: 85,
    attendance: 92,
    leadership: 70,
    technical: 88,
    communication: 75,
    problemSolving: 85,
    teamwork: 82,
    creativity: 72,
    adaptability: 80,
    reliability: 88
  }
];

function TestIntegration() {
  const [testStatus, setTestStatus] = useState({});
  const [isRunning, setIsRunning] = useState(false);

  // Test health check
  const testHealthCheck = async () => {
    try {
      const response = await fetch('https://web-production-4066.up.railway.app/health');
      const data = await response.json();
      return {
        success: data.status === 'healthy',
        message: `Service status: ${data.status}`,
        data
      };
    } catch (error) {
      return {
        success: false,
        message: `Health check failed: ${error.message}`,
        error
      };
    }
  };

  // Test single analysis
  const testSingleAnalysis = async () => {
    try {
      const employee = SAMPLE_EMPLOYEES[0];
      const response = await fetch('https://web-production-4066.up.railway.app/api/v1/llm/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          employee_data: {
            employee_id: employee.id,
            name: employee.name,
            department: employee.department,
            position: employee.position,
            performance_data: {
              목표달성률: employee.goalAchievement,
              프로젝트성공률: employee.projectSuccess,
              고객만족도: employee.customerSatisfaction,
              출근율: employee.attendance
            },
            competencies: {
              리더십: employee.leadership,
              기술력: employee.technical,
              커뮤니케이션: employee.communication,
              문제해결: employee.problemSolving,
              팀워크: employee.teamwork,
              창의성: employee.creativity,
              적응력: employee.adaptability,
              성실성: employee.reliability
            }
          },
          analysis_type: 'comprehensive',
          include_recommendations: true
        })
      });
      
      const data = await response.json();
      return {
        success: response.ok,
        message: response.ok ? 
          `Analysis completed for ${employee.name}: AI Score ${data.ai_score}, Grade ${data.grade}` :
          `Analysis failed: ${data.detail}`,
        data
      };
    } catch (error) {
      return {
        success: false,
        message: `Single analysis test failed: ${error.message}`,
        error
      };
    }
  };

  // Run all tests
  const runAllTests = async () => {
    setIsRunning(true);
    setTestStatus({});

    const tests = [
      { name: 'Health Check', fn: testHealthCheck },
      { name: 'Single Employee Analysis', fn: testSingleAnalysis }
    ];

    for (const test of tests) {
      setTestStatus(prev => ({
        ...prev,
        [test.name]: { status: 'running', message: 'Testing...' }
      }));

      const result = await test.fn();
      
      setTestStatus(prev => ({
        ...prev,
        [test.name]: {
          status: result.success ? 'passed' : 'failed',
          message: result.message,
          data: result.data
        }
      }));

      // Wait a bit between tests
      await new Promise(resolve => setTimeout(resolve, 1000));
    }

    setIsRunning(false);
  };

  return (
    <div style={{ padding: '20px', maxWidth: '1400px', margin: '0 auto' }}>
      <h1>EHR-AIRISS Integration Test</h1>
      
      <div style={{ marginBottom: '30px', padding: '20px', background: '#f5f7fa', borderRadius: '8px' }}>
        <h2>Test Suite</h2>
        <button 
          onClick={runAllTests}
          disabled={isRunning}
          style={{
            padding: '10px 20px',
            background: isRunning ? '#ccc' : '#10b981',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: isRunning ? 'not-allowed' : 'pointer',
            fontSize: '16px'
          }}
        >
          {isRunning ? 'Running Tests...' : 'Run All Tests'}
        </button>

        {Object.keys(testStatus).length > 0 && (
          <div style={{ marginTop: '20px' }}>
            {Object.entries(testStatus).map(([name, result]) => (
              <div 
                key={name}
                style={{
                  padding: '10px',
                  marginBottom: '10px',
                  background: 'white',
                  borderRadius: '6px',
                  borderLeft: `4px solid ${
                    result.status === 'passed' ? '#10b981' :
                    result.status === 'failed' ? '#ef4444' : '#fbbf24'
                  }`
                }}
              >
                <strong>{name}:</strong> {result.message}
                {result.status === 'passed' && result.data && (
                  <details style={{ marginTop: '10px' }}>
                    <summary style={{ cursor: 'pointer' }}>View Response</summary>
                    <pre style={{ 
                      marginTop: '10px', 
                      padding: '10px', 
                      background: '#f5f7fa',
                      borderRadius: '4px',
                      fontSize: '12px',
                      overflow: 'auto'
                    }}>
                      {JSON.stringify(result.data, null, 2)}
                    </pre>
                  </details>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      <div>
        <h2>Live Integration Component</h2>
        <EHRAirissIntegration employees={SAMPLE_EMPLOYEES} />
      </div>
    </div>
  );
}

export default TestIntegration;