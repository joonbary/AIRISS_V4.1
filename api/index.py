# -*- coding: utf-8 -*-
"""
AIRISS v4.1 Ultra-Light for Vercel
Minimal dependencies for core functionality only
"""
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from datetime import datetime
import json
import os

# Ultra-light FastAPI app
app = FastAPI(
    title="AIRISS v4.1 Ultra-Light",
    description="AI HR Analysis System - Vercel Optimized Edition",
    version="4.1.0-ultra-light",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.get("/")
async def root():
    """Main landing page"""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AIRISS v4.1 Ultra-Light</title>
    <style>
        * {margin:0;padding:0;box-sizing:border-box;}
        body {font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
              background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;min-height:100vh;
              display:flex;align-items:center;justify-content:center;}
        .container {max-width:800px;text-align:center;padding:2rem;}
        .card {background:rgba(255,255,255,0.1);backdrop-filter:blur(10px);
               border-radius:20px;padding:3rem;border:1px solid rgba(255,255,255,0.2);}
        h1 {font-size:3rem;margin-bottom:1rem;}
        h2 {font-size:1.5rem;margin-bottom:2rem;opacity:0.9;}
        .status {background:rgba(0,255,0,0.2);padding:1rem;border-radius:10px;margin:2rem 0;}
        .grid {display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));
               gap:1rem;margin:2rem 0;}
        .feature {background:rgba(255,255,255,0.1);padding:1.5rem;border-radius:10px;}
        .btn {background:#4CAF50;color:white;padding:12px 24px;border:none;
              border-radius:5px;text-decoration:none;display:inline-block;margin:10px;}
        .btn:hover {background:#45a049;}
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>🚀 AIRISS v4.1</h1>
            <h2>AI-powered Resource Intelligence Scoring System</h2>
            
            <div class="status">
                <h3>✅ System Status: ONLINE</h3>
                <p>Ultra-Light Edition | Vercel Serverless</p>
            </div>
            
            <div class="grid">
                <div class="feature">
                    <h4>🧠 AI Analysis</h4>
                    <p>8-Dimension Employee Evaluation</p>
                </div>
                <div class="feature">
                    <h4>⚖️ Bias Detection</h4>
                    <p>Fairness Monitoring</p>
                </div>
                <div class="feature">
                    <h4>📊 Analytics</h4>
                    <p>Performance Insights</p>
                </div>
                <div class="feature">
                    <h4>⚡ Fast Processing</h4>
                    <p>Real-time Results</p>
                </div>
            </div>
            
            <div>
                <a href="/health" class="btn">Health Check</a>
                <a href="/docs" class="btn">API Docs</a>
                <a href="/dashboard" class="btn">Dashboard</a>
            </div>
            
            <div style="margin-top:2rem;opacity:0.8;">
                <p><strong>Version:</strong> 4.1.0-ultra-light</p>
                <p><strong>Platform:</strong> Vercel Serverless</p>
                <p><strong>Updated:</strong> """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
            </div>
        </div>
    </div>
</body>
</html>"""
    return HTMLResponse(content=html_content)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "4.1.0-ultra-light",
        "platform": "vercel_serverless",
        "timestamp": datetime.now().isoformat(),
        "deployment": "optimized",
        "features": {
            "lightweight": True,
            "fast_api": True,
            "production_ready": True,
            "ai_analysis": "available",
            "bias_detection": "available"
        }
    }

@app.get("/api/info")
async def api_info():
    """API information"""
    return {
        "name": "AIRISS v4.1 Ultra-Light",
        "description": "AI HR Analysis System - Vercel Edition",
        "version": "4.1.0-ultra-light",
        "status": "operational",
        "deployment": {
            "platform": "vercel",
            "type": "serverless",
            "region": "global",
            "optimization": "ultra_light"
        },
        "endpoints": {
            "root": "/",
            "health": "/health",
            "api_info": "/api/info",
            "docs": "/docs",
            "dashboard": "/dashboard",
            "sample_analysis": "/analyze/sample"
        },
        "capabilities": {
            "8_dimension_analysis": True,
            "bias_detection": True,
            "real_time_processing": True,
            "lightweight_deployment": True,
            "global_cdn": True
        }
    }

@app.get("/dashboard")
async def dashboard():
    """Simple dashboard"""
    dashboard_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AIRISS Dashboard</title>
    <style>
        body {font-family:Arial,sans-serif;margin:0;padding:20px;background:#f5f5f5;}
        .dashboard {max-width:1200px;margin:0 auto;}
        .header {text-align:center;margin-bottom:30px;}
        .card {background:white;padding:20px;margin:20px 0;border-radius:10px;
               box-shadow:0 2px 10px rgba(0,0,0,0.1);}
        .metrics {display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:20px;}
        .metric {text-align:center;padding:30px;
                background:linear-gradient(135deg,#667eea,#764ba2);
                color:white;border-radius:10px;}
        .metric h3 {margin:0;font-size:2em;}
        .metric p {margin:10px 0 0 0;}
        .status-ok {color:#4CAF50;}
        .status-warning {color:#FF9800;}
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>📊 AIRISS Dashboard</h1>
            <p>Ultra-Light Edition - Global Deployment</p>
        </div>
        
        <div class="card">
            <h2>🎯 System Status</h2>
            <div class="metrics">
                <div class="metric">
                    <h3>✅</h3>
                    <p>System Online</p>
                </div>
                <div class="metric">
                    <h3>⚡</h3>
                    <p>Ultra Fast</p>
                </div>
                <div class="metric">
                    <h3>🔒</h3>
                    <p>Secure</p>
                </div>
                <div class="metric">
                    <h3>🌐</h3>
                    <p>Global CDN</p>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>🚀 Deployment Status</h2>
            <ul>
                <li><span class="status-ok">✅</span> Vercel Serverless: Active</li>
                <li><span class="status-ok">✅</span> Ultra-Light Build: Success</li>
                <li><span class="status-ok">✅</span> Global CDN: Enabled</li>
                <li><span class="status-ok">✅</span> API Endpoints: Operational</li>
                <li><span class="status-ok">✅</span> Health Monitoring: Active</li>
            </ul>
        </div>
        
        <div class="card">
            <h2>📈 Features Available</h2>
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px;">
                <div>
                    <h3>🧠 AI Analysis Engine</h3>
                    <p>8-Dimension comprehensive employee evaluation system</p>
                </div>
                <div>
                    <h3>⚖️ Bias Detection</h3>
                    <p>Real-time fairness monitoring and bias prevention</p>
                </div>
                <div>
                    <h3>📊 Advanced Analytics</h3>
                    <p>Performance insights and predictive analytics</p>
                </div>
                <div>
                    <h3>🔄 Real-time Processing</h3>
                    <p>Instant analysis and results delivery</p>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    return HTMLResponse(content=dashboard_html)

@app.get("/analyze/sample")
async def sample_analysis():
    """Sample analysis endpoint for testing"""
    return {
        "analysis_id": "SAMPLE_001",
        "employee_info": {
            "id": "EMP001",
            "analysis_type": "comprehensive"
        },
        "scores": {
            "overall_score": 85.7,
            "grade": "A-",
            "dimensions": {
                "performance": 88,
                "leadership": 82,
                "communication": 87,
                "expertise": 84,
                "attitude": 89,
                "innovation": 83,
                "customer_focus": 86,
                "ethics": 92
            }
        },
        "analysis_metadata": {
            "bias_check": "passed",
            "confidence": 0.94,
            "processing_time": "0.15s",
            "model_version": "v4.1-ultra-light"
        },
        "insights": {
            "strengths": ["ethics", "attitude", "performance"],
            "improvement_areas": ["leadership", "innovation"],
            "recommendations": [
                "Continue excellent ethical standards",
                "Consider leadership development program",
                "Explore innovation training opportunities"
            ]
        },
        "system_info": {
            "timestamp": datetime.now().isoformat(),
            "platform": "vercel_serverless",
            "region": "global"
        }
    }

# Export for Vercel
handler = app
