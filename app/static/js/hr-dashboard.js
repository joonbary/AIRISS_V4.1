// HR Dashboard React Component
const { useState, useEffect } = React;
const { Card, Row, Col, Statistic, Table, Tag, Progress, Spin, Alert, Typography, Divider, Space, Tooltip } = antd;
const { Title, Text, Paragraph } = Typography;
const { Column, ColumnGroup } = Table;
const { Chart, registerables } = ChartJS;

// Chart.js 등록
Chart.register(...registerables);

const HRDashboard = () => {
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState(null);
    const [error, setError] = useState(null);
    const [selectedEmployee, setSelectedEmployee] = useState(null);

    useEffect(() => {
        fetchDashboardData();
    }, []);

    const fetchDashboardData = async () => {
        try {
            setLoading(true);
            const response = await fetch('/api/v1/hr-dashboard/stats');
            if (!response.ok) throw new Error('데이터 로딩 실패');
            const result = await response.json();
            setData(result);
            setError(null);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const renderPromotionCandidates = () => {
        if (!data?.promotion_candidates) return null;
        
        const { count, candidates, has_candidates } = data.promotion_candidates;
        
        if (!has_candidates) {
            return (
                <Card title="승진 후보자 예측" className="dashboard-card">
                    <Alert 
                        message="현재 승진 후보자가 없습니다"
                        description="평가등급, 근속연수, 역량점수, 리더십 등을 종합 평가한 결과 현재 승진 기준(70점 이상)을 충족하는 직원이 없습니다."
                        type="info"
                        showIcon
                    />
                </Card>
            );
        }

        const columns = [
            {
                title: '직원명',
                dataIndex: 'name',
                key: 'name',
                render: (text, record) => (
                    <a onClick={() => setSelectedEmployee(record.uid)}>{text}</a>
                )
            },
            {
                title: '부서',
                dataIndex: 'department',
                key: 'department'
            },
            {
                title: '직급',
                dataIndex: 'position',
                key: 'position'
            },
            {
                title: '승진점수',
                dataIndex: 'score',
                key: 'score',
                render: score => (
                    <Progress 
                        percent={score} 
                        size="small" 
                        status={score >= 90 ? 'success' : score >= 70 ? 'normal' : 'exception'}
                    />
                )
            },
            {
                title: '판단 사유',
                dataIndex: 'reasons',
                key: 'reasons',
                width: 300,
                render: reasons => (
                    <Space direction="vertical" size="small">
                        {reasons.map((reason, idx) => (
                            <Tag key={idx} color="blue">{reason}</Tag>
                        ))}
                    </Space>
                )
            }
        ];

        return (
            <Card 
                title={`승진 후보자 예측 (${count}명)`} 
                className="dashboard-card"
                extra={<Tag color="green">AI 분석 완료</Tag>}
            >
                <Table 
                    dataSource={candidates}
                    columns={columns}
                    pagination={false}
                    size="small"
                    rowKey="uid"
                />
            </Card>
        );
    };

    const renderTopTalents = () => {
        if (!data?.top_talents) return null;
        
        const { count, employees, has_talents } = data.top_talents;

        const columns = [
            {
                title: '순위',
                key: 'rank',
                render: (_, __, index) => index + 1
            },
            {
                title: '직원명',
                dataIndex: 'name',
                key: 'name'
            },
            {
                title: '부서',
                dataIndex: 'department',
                key: 'department'
            },
            {
                title: '등급',
                dataIndex: 'grade',
                key: 'grade',
                render: grade => (
                    <Tag color={grade === 'S' ? 'gold' : grade === 'A' ? 'green' : 'blue'}>
                        {grade}
                    </Tag>
                )
            },
            {
                title: '종합점수',
                dataIndex: 'score',
                key: 'score',
                render: score => `${score}점`
            },
            {
                title: '판단 사유',
                dataIndex: 'reasons',
                key: 'reasons',
                render: reasons => (
                    <Tooltip title={
                        <div>
                            {reasons.map((r, i) => <div key={i}>• {r}</div>)}
                        </div>
                    }>
                        <Space wrap size="small">
                            {reasons.slice(0, 2).map((reason, idx) => (
                                <Tag key={idx} color="purple">{reason}</Tag>
                            ))}
                            {reasons.length > 2 && <Tag>+{reasons.length - 2}개</Tag>}
                        </Space>
                    </Tooltip>
                )
            }
        ];

        return (
            <Card 
                title={`Top Talent (${count}명)`}
                className="dashboard-card"
                extra={
                    <Space>
                        <Text type="secondary">기준: 성과, 잠재력, 역량, 혁신성</Text>
                        <Tag color="purple">핵심인재</Tag>
                    </Space>
                }
            >
                <Table 
                    dataSource={employees}
                    columns={columns}
                    pagination={false}
                    size="small"
                    rowKey="uid"
                />
            </Card>
        );
    };

    const renderRiskEmployees = () => {
        if (!data?.risk_employees) return null;
        
        const { count, employees, high_risk_count, medium_risk_count } = data.risk_employees;

        const columns = [
            {
                title: '직원명',
                dataIndex: 'name',
                key: 'name'
            },
            {
                title: '부서',
                dataIndex: 'department',
                key: 'department'
            },
            {
                title: '위험도',
                dataIndex: 'risk_level',
                key: 'risk_level',
                render: level => (
                    <Tag color={level === 'high' ? 'red' : 'orange'}>
                        {level === 'high' ? '높음' : '보통'}
                    </Tag>
                )
            },
            {
                title: '위험점수',
                dataIndex: 'risk_score',
                key: 'risk_score',
                render: score => (
                    <Progress 
                        percent={score} 
                        size="small" 
                        status="exception"
                        strokeColor={score >= 70 ? '#ff4d4f' : '#faad14'}
                    />
                )
            },
            {
                title: '관리 필요 사유',
                dataIndex: 'reasons',
                key: 'reasons',
                width: 350,
                render: reasons => (
                    <Space wrap size="small">
                        {reasons.map((reason, idx) => (
                            <Tag key={idx} color={reason.includes('부진') || reason.includes('위험') ? 'red' : 'orange'}>
                                {reason}
                            </Tag>
                        ))}
                    </Space>
                )
            }
        ];

        return (
            <Card 
                title={`관리 필요 인력 (총 ${count}명)`}
                className="dashboard-card"
                extra={
                    <Space>
                        <Tag color="red">고위험 {high_risk_count}명</Tag>
                        <Tag color="orange">중위험 {medium_risk_count}명</Tag>
                    </Space>
                }
            >
                <Paragraph type="secondary">
                    성과, 근태, 이직위험도, 역량 등을 종합 평가하여 관리가 필요한 인력을 식별합니다.
                </Paragraph>
                <Table 
                    dataSource={employees}
                    columns={columns}
                    pagination={{ pageSize: 5 }}
                    size="small"
                    rowKey="uid"
                />
            </Card>
        );
    };

    const renderGradeDistribution = () => {
        if (!data?.grade_distribution) return null;

        const chartData = {
            labels: data.grade_distribution.map(g => `${g.grade}등급`),
            datasets: [{
                label: '인원수',
                data: data.grade_distribution.map(g => g.count),
                backgroundColor: [
                    'rgba(255, 215, 0, 0.8)',  // S - Gold
                    'rgba(76, 175, 80, 0.8)',   // A - Green
                    'rgba(33, 150, 243, 0.8)',  // B - Blue
                    'rgba(255, 152, 0, 0.8)',   // C - Orange
                    'rgba(158, 158, 158, 0.8)'  // D - Gray
                ],
                borderColor: [
                    'rgba(255, 215, 0, 1)',
                    'rgba(76, 175, 80, 1)',
                    'rgba(33, 150, 243, 1)',
                    'rgba(255, 152, 0, 1)',
                    'rgba(158, 158, 158, 1)'
                ],
                borderWidth: 2
            }]
        };

        const options = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: '등급별 인원 분포',
                    font: {
                        size: 16
                    }
                },
                tooltip: {
                    callbacks: {
                        afterLabel: function(context) {
                            const grade = data.grade_distribution[context.dataIndex];
                            return `비율: ${grade.percentage}%`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: '인원수'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: '평가 등급'
                    }
                }
            }
        };

        return (
            <Card title="평가 등급 분포" className="dashboard-card">
                <div style={{ height: '300px' }}>
                    <canvas id="gradeChart"></canvas>
                </div>
                <Divider />
                <Row gutter={16}>
                    {data.grade_distribution.map(grade => (
                        <Col span={4} key={grade.grade}>
                            <Statistic
                                title={`${grade.grade}등급`}
                                value={grade.count}
                                suffix={`명 (${grade.percentage}%)`}
                            />
                        </Col>
                    ))}
                </Row>
            </Card>
        );
    };

    useEffect(() => {
        if (data?.grade_distribution) {
            const ctx = document.getElementById('gradeChart');
            if (ctx) {
                const chart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: data.grade_distribution.map(g => `${g.grade}등급`),
                        datasets: [{
                            label: '인원수',
                            data: data.grade_distribution.map(g => g.count),
                            backgroundColor: [
                                'rgba(255, 215, 0, 0.8)',
                                'rgba(76, 175, 80, 0.8)',
                                'rgba(33, 150, 243, 0.8)',
                                'rgba(255, 152, 0, 0.8)',
                                'rgba(158, 158, 158, 0.8)'
                            ],
                            borderColor: [
                                'rgba(255, 215, 0, 1)',
                                'rgba(76, 175, 80, 1)',
                                'rgba(33, 150, 243, 1)',
                                'rgba(255, 152, 0, 1)',
                                'rgba(158, 158, 158, 1)'
                            ],
                            borderWidth: 2
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                display: false
                            },
                            title: {
                                display: true,
                                text: '등급별 인원 분포',
                                font: {
                                    size: 16
                                }
                            },
                            tooltip: {
                                callbacks: {
                                    afterLabel: function(context) {
                                        const grade = data.grade_distribution[context.dataIndex];
                                        return `비율: ${grade.percentage}%`;
                                    }
                                }
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                title: {
                                    display: true,
                                    text: '인원수'
                                }
                            },
                            x: {
                                title: {
                                    display: true,
                                    text: '평가 등급'
                                }
                            }
                        }
                    }
                });

                return () => {
                    chart.destroy();
                };
            }
        }
    }, [data]);

    if (loading) {
        return (
            <div style={{ textAlign: 'center', padding: '50px' }}>
                <Spin size="large" tip="데이터 로딩중..." />
            </div>
        );
    }

    if (error) {
        return (
            <Alert
                message="데이터 로드 실패"
                description={error}
                type="error"
                showIcon
            />
        );
    }

    return (
        <div className="hr-dashboard">
            <Title level={2}>HR 대시보드</Title>
            <Paragraph>
                AI 기반 인재 분석 및 예측 시스템
            </Paragraph>
            
            <Row gutter={[16, 16]}>
                <Col span={24}>
                    <Card>
                        <Row gutter={16}>
                            <Col span={6}>
                                <Statistic 
                                    title="전체 직원" 
                                    value={data?.total_employees || 0} 
                                    suffix="명"
                                />
                            </Col>
                            <Col span={6}>
                                <Statistic 
                                    title="승진 후보자" 
                                    value={data?.promotion_candidates?.count || 0} 
                                    suffix="명"
                                    valueStyle={{ color: '#3f8600' }}
                                />
                            </Col>
                            <Col span={6}>
                                <Statistic 
                                    title="핵심 인재" 
                                    value={data?.top_talents?.count || 0} 
                                    suffix="명"
                                    valueStyle={{ color: '#722ed1' }}
                                />
                            </Col>
                            <Col span={6}>
                                <Statistic 
                                    title="관리 필요" 
                                    value={data?.risk_employees?.count || 0} 
                                    suffix="명"
                                    valueStyle={{ color: '#cf1322' }}
                                />
                            </Col>
                        </Row>
                    </Card>
                </Col>
            </Row>

            <Row gutter={[16, 16]} style={{ marginTop: '20px' }}>
                <Col span={24}>
                    {renderPromotionCandidates()}
                </Col>
            </Row>

            <Row gutter={[16, 16]} style={{ marginTop: '20px' }}>
                <Col span={24}>
                    {renderTopTalents()}
                </Col>
            </Row>

            <Row gutter={[16, 16]} style={{ marginTop: '20px' }}>
                <Col span={24}>
                    {renderRiskEmployees()}
                </Col>
            </Row>

            <Row gutter={[16, 16]} style={{ marginTop: '20px' }}>
                <Col span={24}>
                    {renderGradeDistribution()}
                </Col>
            </Row>
        </div>
    );
};

// React 렌더링
const root = ReactDOM.createRoot(document.getElementById('hr-dashboard-root'));
root.render(<HRDashboard />);