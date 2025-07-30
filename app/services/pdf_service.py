"""
PDF 생성 서비스
개인별 AI 분석 리포트를 PDF로 생성
"""
import io
import logging
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.platypus.flowables import Flowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Line, Circle, Polygon, String as GraphicsString, Rect
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart, HorizontalBarChart
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics import renderPDF
from reportlab.graphics.widgets.grids import Grid
import math
from typing import Dict, Any, List
import os

logger = logging.getLogger(__name__)

# 한글 폰트 설정
try:
    # Windows 시스템 폰트 경로
    font_paths = [
        r"C:\Windows\Fonts\malgun.ttf",  # 맑은 고딕
        r"C:\Windows\Fonts\NanumGothic.ttf",  # 나눔고딕
        r"C:\Windows\Fonts\gulim.ttc",  # 굴림
    ]
    
    font_registered = False
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont('Korean', font_path))
                font_registered = True
                logger.info(f"한글 폰트 등록 성공: {font_path}")
                break
            except:
                continue
    
    if not font_registered:
        logger.warning("한글 폰트를 찾을 수 없습니다. 기본 폰트를 사용합니다.")
except Exception as e:
    logger.error(f"폰트 등록 오류: {e}")


class HorizontalLine(Flowable):
    """수평선 그리기"""
    def __init__(self, width, color=colors.black, thickness=1):
        Flowable.__init__(self)
        self.width = width
        self.color = color
        self.thickness = thickness
        
    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, 0, self.width, 0)


class ModernCard(Flowable):
    """현대적인 카드 스타일 컨테이너"""
    def __init__(self, width, height, bg_color=colors.white, border_color=colors.lightgrey, corner_radius=8):
        Flowable.__init__(self)
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.border_color = border_color
        self.corner_radius = corner_radius
        
    def draw(self):
        self.canv.setFillColor(self.bg_color)
        self.canv.setStrokeColor(self.border_color)
        self.canv.setLineWidth(1)
        self.canv.roundRect(0, 0, self.width, self.height, self.corner_radius, fill=1, stroke=1)


class IconText(Flowable):
    """아이콘과 텍스트 조합"""
    def __init__(self, icon_char, text, font_name='Korean', text_color=colors.black):
        Flowable.__init__(self)
        self.icon_char = icon_char
        self.text = text
        self.font_name = font_name
        self.text_color = text_color
        self.width = 200
        self.height = 20
        
    def draw(self):
        self.canv.setFont(self.font_name, 12)
        self.canv.setFillColor(self.text_color)
        self.canv.drawString(0, 5, f"{self.icon_char} {self.text}")


class PDFReportGenerator:
    """개인별 AI 분석 리포트 PDF 생성기"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_styles()
        
    def _setup_styles(self):
        """스타일 설정"""
        # 한글 폰트가 등록되었는지 확인
        if 'Korean' in pdfmetrics.getRegisteredFontNames():
            font_name = 'Korean'
        else:
            font_name = 'Helvetica'
            
        # 현대적인 제목 스타일
        self.styles.add(ParagraphStyle(
            name='ModernTitle',
            parent=self.styles['Title'],
            fontName=font_name,
            fontSize=28,
            textColor=colors.white,
            alignment=TA_CENTER,
            spaceAfter=20,
            spaceBefore=20
        ))
        
        # 서브타이틀 스타일
        self.styles.add(ParagraphStyle(
            name='ModernSubtitle',
            parent=self.styles['Normal'],
            fontName=font_name,
            fontSize=14,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER,
            spaceAfter=30
        ))
        
        # 현대적인 섹션 헤딩
        self.styles.add(ParagraphStyle(
            name='ModernHeading',
            parent=self.styles['Heading1'],
            fontName=font_name,
            fontSize=18,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=25,
            leftIndent=15
        ))
        
        # 현대적인 본문 스타일
        self.styles.add(ParagraphStyle(
            name='ModernBody',
            parent=self.styles['Normal'],
            fontName=font_name,
            fontSize=11,
            leading=16,
            alignment=TA_LEFT,
            leftIndent=10,
            textColor=colors.HexColor('#444444')
        ))
        
        # 하이라이트 박스 스타일
        self.styles.add(ParagraphStyle(
            name='HighlightBox',
            parent=self.styles['Normal'],
            fontName=font_name,
            fontSize=12,
            textColor=colors.white,
            alignment=TA_CENTER,
            leftIndent=15,
            rightIndent=15
        ))
        
        # 메트릭 스타일
        self.styles.add(ParagraphStyle(
            name='MetricValue',
            parent=self.styles['Normal'],
            fontName=font_name,
            fontSize=24,
            textColor=colors.HexColor('#1976d2'),
            alignment=TA_CENTER,
            fontWeight='bold'
        ))
        
        # 메트릭 라벨 스타일
        self.styles.add(ParagraphStyle(
            name='MetricLabel',
            parent=self.styles['Normal'],
            fontName=font_name,
            fontSize=10,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER
        ))
        
    def _extract_from_pandas_series(self, value):
        """pandas Series 문자열에서 실제 값 추출"""
        if not isinstance(value, str):
            return str(value)
        
        # pandas Series 형태 감지
        if 'dtype: object' in value:
            import re
            # EMP001과 같은 패턴 추출
            emp_id_match = re.search(r'EMP\d+', value)
            if emp_id_match:
                return emp_id_match.group()
            
            # 한글 이름 패턴 추출 (예: 관리자1, 관리자2)
            name_match = re.search(r'관리자\d+', value)
            if name_match:
                return name_match.group()
            
            # 기타 텍스트 추출 시도
            lines = value.split('\n')
            for line in lines:
                clean_line = line.strip()
                if clean_line and 'uid' not in clean_line and 'Name:' not in clean_line and 'dtype:' not in clean_line:
                    return clean_line
        
        return str(value)
    
    def _clean_employee_data(self, employee_data: Dict[str, Any]) -> Dict[str, Any]:
        """직원 데이터에서 pandas Series 정리 및 누락 정보 보완"""
        cleaned_data = {}
        
        # 기본 정보 정리
        cleaned_data['employee_id'] = self._extract_from_pandas_series(employee_data.get('employee_id', ''))
        cleaned_data['uid'] = self._extract_from_pandas_series(employee_data.get('uid', ''))
        cleaned_data['name'] = employee_data.get('name', '직원')
        
        # 부서/직급 정보 - 원본 데이터에서 추출하거나 기본값 설정
        raw_dept = employee_data.get('department', '')
        raw_pos = employee_data.get('position', '')
        
        # pandas Series에서 부서 정보 추출 시도
        if not raw_dept or raw_dept == '':
            # employee_id나 uid에서 관리자 정보 추출
            uid_info = employee_data.get('uid', '')
            if '관리자' in str(uid_info):
                import re
                manager_match = re.search(r'관리자\d+', str(uid_info))
                if manager_match:
                    cleaned_data['department'] = f"{manager_match.group()} 팀"
                else:
                    cleaned_data['department'] = "관리팀"
            else:
                cleaned_data['department'] = "일반팀"
        else:
            cleaned_data['department'] = self._extract_from_pandas_series(raw_dept)
        
        # 직급 정보
        if not raw_pos or raw_pos == '':
            # 성과 점수에 따른 직급 추정
            final_score = employee_data.get('final_score', 0)
            if final_score >= 90:
                cleaned_data['position'] = "팀장"
            elif final_score >= 80:
                cleaned_data['position'] = "선임"
            elif final_score >= 70:
                cleaned_data['position'] = "대리"
            else:
                cleaned_data['position'] = "사원"
        else:
            cleaned_data['position'] = self._extract_from_pandas_series(raw_pos)
        
        # 나머지 데이터 복사
        for key, value in employee_data.items():
            if key not in cleaned_data:
                cleaned_data[key] = value
                
        return cleaned_data
    
    def _create_modern_header(self, employee_name: str, job_id: str) -> Drawing:
        """현대적인 헤더 생성"""
        drawing = Drawing(450, 120)
        
        # 그라디언트 배경
        bg_rect = Rect(0, 0, 450, 120)
        bg_rect.fillColor = colors.HexColor('#1976d2')
        bg_rect.strokeColor = None
        drawing.add(bg_rect)
        
        # 상단 엑센트
        accent_rect = Rect(0, 100, 450, 20)
        accent_rect.fillColor = colors.HexColor('#0d47a1')
        accent_rect.strokeColor = None
        drawing.add(accent_rect)
        
        # 로고 영역 (사각형)
        logo_rect = Rect(20, 20, 80, 80)
        logo_rect.fillColor = colors.HexColor('#ffffff')
        logo_rect.strokeColor = None
        drawing.add(logo_rect)
        
        # AIRISS 로고 텍스트
        logo_text = GraphicsString(60, 55, "AIRISS")
        logo_text.fontName = 'Korean' if 'Korean' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
        logo_text.fontSize = 12
        logo_text.fillColor = colors.HexColor('#1976d2')
        logo_text.textAnchor = 'middle'
        drawing.add(logo_text)
        
        logo_sub = GraphicsString(60, 40, "v4.0")
        logo_sub.fontName = 'Korean' if 'Korean' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
        logo_sub.fontSize = 8
        logo_sub.fillColor = colors.HexColor('#666666')
        logo_sub.textAnchor = 'middle'
        drawing.add(logo_sub)
        
        # 제목
        title_text = GraphicsString(120, 70, "AI 인재 분석 리포트")
        title_text.fontName = 'Korean' if 'Korean' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
        title_text.fontSize = 20
        title_text.fillColor = colors.white
        drawing.add(title_text)
        
        # 직원명
        name_text = GraphicsString(120, 45, f"대상자: {employee_name}")
        name_text.fontName = 'Korean' if 'Korean' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
        name_text.fontSize = 14
        name_text.fillColor = colors.HexColor('#e3f2fd')
        drawing.add(name_text)
        
        # 날짜
        date_text = GraphicsString(120, 25, f"분석일시: {datetime.now().strftime('%Y년 %m월 %d일')}")
        date_text.fontName = 'Korean' if 'Korean' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
        date_text.fontSize = 10
        date_text.fillColor = colors.HexColor('#e3f2fd')
        drawing.add(date_text)
        
        return drawing

    def generate_employee_report(self, employee_data: Dict[str, Any], job_id: str) -> bytes:
        """개인별 분석 리포트 생성"""
        # 데이터 정리 (pandas Series 처리 및 누락 정보 보완)
        clean_data = self._clean_employee_data(employee_data)
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # 리포트 내용 구성
        story = []
        
        # 현대적인 헤더 추가됨 - 구 제목 페이지 삭제
        
        # 기본 정보 테이블 (정리된 데이터 사용)
        basic_info = [
            ["이름", clean_data.get('name', '')],
            ["사번", clean_data.get('employee_id', '')],
            ["부서", clean_data.get('department', '정보 없음')],
            ["직급", clean_data.get('position', '정보 없음')],
            ["분석일시", datetime.now().strftime("%Y년 %m월 %d일")],
            ["AI 신뢰도", f"{clean_data.get('confidence_score', 85)}%"]
        ]
        
        basic_table = Table(basic_info, colWidths=[3*cm, 10*cm])
        basic_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e3f2fd')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Korean' if 'Korean' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey)
        ]))
        story.append(basic_table)
        story.append(Spacer(1, 0.5*inch))
        
        # AI 종합 평가
        story.append(Paragraph("AI 종합 평가", self.styles['ModernHeading']))
        story.append(HorizontalLine(450, colors.HexColor('#1976d2')))
        story.append(Spacer(1, 0.2*inch))
        
        # 종합 점수와 등급
        score_data = [
            ["AI 종합점수", f"{clean_data.get('final_score', 0):.1f}점"],
            ["등급", clean_data.get('grade', 'B')],
            ["백분위", f"상위 {100 - clean_data.get('percentile_rank', 75)}%"]
        ]
        
        score_table = Table(score_data, colWidths=[3*cm, 10*cm])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#fff3e0')),
            ('BACKGROUND', (1, 0), (1, 0), self._get_grade_color(clean_data.get('grade', 'B'))),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Korean' if 'Korean' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('FONTSIZE', (1, 0), (1, 0), 18),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        story.append(score_table)
        story.append(Spacer(1, 0.5*inch))
        
        # 8대 핵심 역량 분석
        story.append(Paragraph("8대 핵심 역량 분석", self.styles['ModernHeading']))
        story.append(HorizontalLine(450, colors.HexColor('#1976d2')))
        story.append(Spacer(1, 0.2*inch))
        
        # 역량 점수 테이블
        competencies = clean_data.get('competencies', {})
        competency_data = [["역량", "점수", "평가"]]
        
        for comp_name, comp_score in competencies.items():
            evaluation = self._get_competency_evaluation(comp_score)
            competency_data.append([comp_name, f"{comp_score:.1f}", evaluation])
            
        comp_table = Table(competency_data, colWidths=[5*cm, 3*cm, 5*cm])
        comp_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976d2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Korean' if 'Korean' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')])
        ]))
        story.append(comp_table)
        story.append(Spacer(1, 0.3*inch))
        
        # 역량 레이더 차트 추가
        if competencies:
            story.append(Paragraph("역량 레이더 차트", self.styles['ModernHeading']))
            radar_chart = self._create_competency_radar_chart(competencies)
            story.append(radar_chart)
            story.append(Spacer(1, 0.3*inch))
        
        # 강점 및 개선점
        story.append(Paragraph("강점 분석", self.styles['ModernHeading']))
        story.append(HorizontalLine(450, colors.HexColor('#4caf50')))
        story.append(Spacer(1, 0.1*inch))
        
        strengths = clean_data.get('strengths', [])
        for i, strength in enumerate(strengths[:3], 1):
            story.append(Paragraph(f"• {strength}", self.styles['ModernBody']))
            story.append(Spacer(1, 0.1*inch))
            
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph("개발 필요 영역", self.styles['ModernHeading']))
        story.append(HorizontalLine(450, colors.HexColor('#ff9800')))
        story.append(Spacer(1, 0.1*inch))
        
        improvements = clean_data.get('improvements', [])
        for i, improvement in enumerate(improvements[:3], 1):
            story.append(Paragraph(f"• {improvement}", self.styles['ModernBody']))
            story.append(Spacer(1, 0.1*inch))
            
        # 새 페이지
        story.append(PageBreak())
        
        # AI 종합 피드백
        story.append(Paragraph("AI 종합 피드백", self.styles['ModernHeading']))
        story.append(HorizontalLine(450, colors.HexColor('#9c27b0')))
        story.append(Spacer(1, 0.2*inch))
        
        ai_feedback = clean_data.get('ai_feedback') or clean_data.get('feedback', '')
        if ai_feedback:
            story.append(Paragraph(ai_feedback, self.styles['ModernBody']))
        else:
            story.append(Paragraph(
                "직원의 전반적인 성과가 양호하며, 지속적인 성장 가능성이 있습니다. "
                "강점을 더욱 발전시키고 개선 영역에 대한 교육과 멘토링을 통해 "
                "더 높은 성과를 달성할 수 있을 것으로 기대됩니다.",
                self.styles['ModernBody']
            ))
        story.append(Spacer(1, 0.5*inch))
        
        # 경력 개발 추천
        story.append(Paragraph("경력 개발 추천", self.styles['ModernHeading']))
        story.append(HorizontalLine(450, colors.HexColor('#00bcd4')))
        story.append(Spacer(1, 0.2*inch))
        
        career_recommendations = clean_data.get('career_recommendation', [])
        if career_recommendations:
            for rec in career_recommendations[:3]:
                story.append(Paragraph(f"• {rec}", self.styles['ModernBody']))
                story.append(Spacer(1, 0.1*inch))
        else:
            story.append(Paragraph("• 현재 직무에서의 전문성 강화", self.styles['ModernBody']))
            story.append(Paragraph("• 리더십 역량 개발 프로그램 참여", self.styles['ModernBody']))
            story.append(Paragraph("• 크로스 펑셔널 프로젝트 참여", self.styles['ModernBody']))
            
        story.append(Spacer(1, 0.5*inch))
        
        # 교육 추천
        story.append(Paragraph("추천 교육 프로그램", self.styles['ModernHeading']))
        story.append(HorizontalLine(450, colors.HexColor('#795548')))
        story.append(Spacer(1, 0.2*inch))
        
        education_suggestions = clean_data.get('education_suggestion', [])
        if education_suggestions:
            for edu in education_suggestions[:3]:
                story.append(Paragraph(f"• {edu}", self.styles['ModernBody']))
                story.append(Spacer(1, 0.1*inch))
        else:
            story.append(Paragraph("• 리더십 교육 프로그램", self.styles['ModernBody']))
            story.append(Paragraph("• 전문 기술 심화 과정", self.styles['ModernBody']))
            story.append(Paragraph("• 커뮤니케이션 스킬 향상 워크샵", self.styles['ModernBody']))
            
        # Footer
        story.append(Spacer(1, 1*inch))
        story.append(HorizontalLine(450, color=colors.grey))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph(
            f"본 리포트는 AIRISS v4.0 AI 시스템에 의해 생성되었습니다. (Job ID: {job_id})",
            ParagraphStyle(
                name='Footer',
                parent=self.styles['Normal'],
                fontSize=8,
                textColor=colors.grey,
                alignment=TA_CENTER
            )
        ))
        
        # PDF 생성
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
        
    def _get_grade_color(self, grade: str) -> colors.Color:
        """등급별 색상 반환"""
        grade_colors = {
            'S': colors.HexColor('#9c27b0'),
            'A+': colors.HexColor('#2196f3'),
            'A': colors.HexColor('#03a9f4'),
            'B+': colors.HexColor('#4caf50'),
            'B': colors.HexColor('#8bc34a'),
            'C': colors.HexColor('#ff9800'),
            'D': colors.HexColor('#f44336')
        }
        return grade_colors.get(grade, colors.HexColor('#757575'))
        
    def _get_competency_evaluation(self, score: float) -> str:
        """역량 점수에 따른 평가 반환"""
        if score >= 90:
            return "탁월"
        elif score >= 80:
            return "우수"
        elif score >= 70:
            return "양호"
        elif score >= 60:
            return "보통"
        else:
            return "개선필요"
    
    def _create_competency_radar_chart(self, competencies: Dict[str, float]) -> Drawing:
        """역량 레이더 차트 생성"""
        drawing = Drawing(400, 300)
        
        # 차트 중심점과 반지름
        center_x, center_y = 200, 150
        max_radius = 100
        
        # 역량 목록과 점수 정리
        comp_list = list(competencies.items())
        if not comp_list:
            return drawing
            
        num_competencies = len(comp_list)
        angle_step = 2 * math.pi / num_competencies
        
        # 배경 원과 격자
        for i in range(1, 6):  # 20, 40, 60, 80, 100 점 원
            radius = max_radius * i / 5
            circle = Circle(center_x, center_y, radius)
            circle.strokeColor = colors.lightgrey
            circle.fillColor = None
            circle.strokeWidth = 0.5
            drawing.add(circle)
        
        # 각 역량으로의 선
        for i in range(num_competencies):
            angle = i * angle_step - math.pi / 2  # -90도에서 시작
            end_x = center_x + max_radius * math.cos(angle)
            end_y = center_y + max_radius * math.sin(angle)
            
            line = Line(center_x, center_y, end_x, end_y)
            line.strokeColor = colors.lightgrey
            line.strokeWidth = 0.5
            drawing.add(line)
        
        # 레이더 차트 데이터 포인트
        points = []
        for i, (comp_name, score) in enumerate(comp_list):
            angle = i * angle_step - math.pi / 2
            # 점수를 0-100 범위로 정규화
            normalized_score = min(max(score, 0), 100) / 100
            radius = max_radius * normalized_score
            
            point_x = center_x + radius * math.cos(angle)
            point_y = center_y + radius * math.sin(angle)
            points.extend([point_x, point_y])
        
        # 레이더 차트 다각형 그리기
        if len(points) >= 6:  # 최소 3개 역량 필요
            polygon = Polygon(points)
            polygon.fillColor = colors.HexColor('#1976d2')
            polygon.fillOpacity = 0.3
            polygon.strokeColor = colors.HexColor('#1976d2')
            polygon.strokeWidth = 2
            drawing.add(polygon)
        
        # 역량 라벨 추가
        for i, (comp_name, score) in enumerate(comp_list):
            angle = i * angle_step - math.pi / 2
            label_radius = max_radius + 20
            label_x = center_x + label_radius * math.cos(angle)
            label_y = center_y + label_radius * math.sin(angle)
            
            # 한글 폰트 사용 가능한지 확인
            font_name = 'Korean' if 'Korean' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
            
            label = GraphicsString(label_x, label_y, f"{comp_name}\n{score:.1f}")
            label.fontName = font_name
            label.fontSize = 8
            label.fillColor = colors.black
            label.textAnchor = 'middle'
            drawing.add(label)
        
        return drawing
    
    def _create_competency_bar_chart(self, competencies: Dict[str, float]) -> Drawing:
        """역량 바 차트 생성"""
        drawing = Drawing(400, 200)
        
        if not competencies:
            return drawing
            
        # 바 차트 생성
        bc = HorizontalBarChart()
        bc.x = 50
        bc.y = 30
        bc.height = 140
        bc.width = 300
        
        # 데이터 준비
        comp_names = list(competencies.keys())
        comp_scores = [list(competencies.values())]
        
        bc.data = comp_scores
        bc.categoryAxis.categoryNames = comp_names
        
        # 스타일링
        bc.bars[0].fillColor = colors.HexColor('#1976d2')
        bc.categoryAxis.labels.fontName = 'Korean' if 'Korean' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
        bc.categoryAxis.labels.fontSize = 8
        bc.valueAxis.labels.fontSize = 8
        bc.valueAxis.visibleGrid = True
        
        drawing.add(bc)
        return drawing
    
    def _create_score_donut_chart(self, final_score: float) -> Drawing:
        """종합 점수 도널 차트 생성"""
        drawing = Drawing(200, 200)
        
        # 도널 차트 생성
        pie = Pie()
        pie.x = 50
        pie.y = 50
        pie.width = 100
        pie.height = 100
        
        # 점수를 백분율로 바꿀
        score_percent = min(final_score, 100)
        remaining_percent = 100 - score_percent
        
        pie.data = [score_percent, remaining_percent]
        pie.labels = ['', '']
        pie.slices[0].fillColor = colors.HexColor('#4caf50')
        pie.slices[1].fillColor = colors.HexColor('#e0e0e0')
        pie.slices[0].strokeColor = colors.white
        pie.slices[1].strokeColor = colors.white
        pie.slices[0].strokeWidth = 2
        pie.slices[1].strokeWidth = 2
        
        # 내부 원 (도널 효과)
        inner_circle = Circle(100, 100, 35)
        inner_circle.fillColor = colors.white
        inner_circle.strokeColor = None
        drawing.add(inner_circle)
        
        drawing.add(pie)
        
        # 중앙에 점수 표시
        score_text = GraphicsString(100, 95, f"{final_score:.1f}")
        score_text.fontName = 'Korean' if 'Korean' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
        score_text.fontSize = 16
        score_text.fillColor = colors.HexColor('#2c3e50')
        score_text.textAnchor = 'middle'
        drawing.add(score_text)
        
        return drawing
    
    def _create_grade_indicator(self, grade: str) -> Drawing:
        """등급 인디케이터 생성"""
        drawing = Drawing(100, 60)
        
        # 색상 매핑
        grade_colors = {
            'S': colors.HexColor('#9c27b0'),
            'A+': colors.HexColor('#2196f3'),
            'A': colors.HexColor('#03a9f4'),
            'B+': colors.HexColor('#4caf50'),
            'B': colors.HexColor('#8bc34a'),
            'C': colors.HexColor('#ff9800'),
            'D': colors.HexColor('#f44336')
        }
        
        # 배경 원
        bg_circle = Circle(50, 30, 25)
        bg_circle.fillColor = grade_colors.get(grade, colors.HexColor('#757575'))
        bg_circle.strokeColor = None
        drawing.add(bg_circle)
        
        # 등급 표시
        grade_text = GraphicsString(50, 25, grade)
        grade_text.fontName = 'Korean' if 'Korean' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
        grade_text.fontSize = 18
        grade_text.fillColor = colors.white
        grade_text.textAnchor = 'middle'
        drawing.add(grade_text)
        
        return drawing