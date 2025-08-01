"""
텍스트 정제 유틸리티
Text cleaning utilities for Korean and English text
"""
import re
from typing import Optional, List
import unicodedata


class TextCleaner:
    """텍스트 정제 클래스"""
    
    # 한국어 불용어 리스트 (필요시 확장)
    KOREAN_STOPWORDS = {
        '의', '가', '이', '은', '들', '는', '좀', '잘', '걍', '과', '도', 
        '를', '으로', '자', '에', '와', '한', '하다', '을', '를', '있다',
        '되다', '이다', '그', '그리고', '그러나', '하지만', '때문에'
    }
    
    # 영어 불용어 리스트
    ENGLISH_STOPWORDS = {
        'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
        'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
        'to', 'was', 'will', 'with', 'the', 'this', 'but', 'they', 'have'
    }
    
    def __init__(self, 
                 remove_special_chars: bool = True,
                 normalize_whitespace: bool = True,
                 remove_stopwords: bool = False,
                 min_length: int = 10,
                 max_length: int = 1000):
        """
        텍스트 정제기 초기화
        
        Args:
            remove_special_chars: 특수문자 제거 여부
            normalize_whitespace: 공백 정규화 여부
            remove_stopwords: 불용어 제거 여부
            min_length: 최소 문장 길이
            max_length: 최대 문장 길이
        """
        self.remove_special_chars = remove_special_chars
        self.normalize_whitespace = normalize_whitespace
        self.remove_stopwords = remove_stopwords
        self.min_length = min_length
        self.max_length = max_length
    
    def clean(self, text: Optional[str]) -> Optional[str]:
        """
        텍스트 정제 메인 함수
        
        Args:
            text: 정제할 텍스트
            
        Returns:
            정제된 텍스트 또는 None
        """
        if not text or not isinstance(text, str):
            return None
            
        # 1. Unicode 정규화
        text = unicodedata.normalize('NFKC', text)
        
        # 2. HTML 태그 제거
        text = re.sub(r'<[^>]+>', '', text)
        
        # 3. 특수문자 처리
        if self.remove_special_chars:
            # 한글, 영문, 숫자, 기본 문장부호만 유지
            text = re.sub(r'[^\w\s가-힣a-zA-Z0-9.,!?;:\-\(\)]', ' ', text)
        
        # 4. 공백 정규화
        if self.normalize_whitespace:
            # 연속된 공백을 하나로
            text = re.sub(r'\s+', ' ', text)
            # 문장부호 앞뒤 공백 정리
            text = re.sub(r'\s*([.,!?;:])\s*', r'\1 ', text)
            text = text.strip()
        
        # 5. 길이 검증
        if len(text) < self.min_length:
            return None
        if len(text) > self.max_length:
            text = text[:self.max_length] + "..."
        
        # 6. 불용어 제거 (선택적)
        if self.remove_stopwords:
            text = self._remove_stopwords(text)
        
        return text.strip()
    
    def _remove_stopwords(self, text: str) -> str:
        """불용어 제거"""
        words = text.split()
        filtered_words = []
        
        for word in words:
            # 한국어와 영어 불용어 체크
            if (word.lower() not in self.ENGLISH_STOPWORDS and 
                word not in self.KOREAN_STOPWORDS):
                filtered_words.append(word)
        
        return ' '.join(filtered_words)
    
    def clean_batch(self, texts: List[Optional[str]]) -> List[Optional[str]]:
        """
        여러 텍스트 일괄 정제
        
        Args:
            texts: 정제할 텍스트 리스트
            
        Returns:
            정제된 텍스트 리스트
        """
        return [self.clean(text) for text in texts]
    
    def extract_sentences(self, text: str) -> List[str]:
        """
        텍스트에서 문장 추출
        
        Args:
            text: 원본 텍스트
            
        Returns:
            문장 리스트
        """
        if not text:
            return []
        
        # 한국어와 영어 문장 종결 부호 기준으로 분리
        sentences = re.split(r'[.!?。！？]+', text)
        
        # 빈 문장 제거 및 정제
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def normalize_year_format(self, opinions_dict: dict) -> dict:
        """
        연도별 평가의견 딕셔너리 정규화
        
        Args:
            opinions_dict: 연도별 평가의견 딕셔너리
            
        Returns:
            정규화된 딕셔너리
        """
        normalized = {}
        
        for key, value in opinions_dict.items():
            # 연도 추출 (다양한 형식 지원)
            year_match = re.search(r'(\d{4})', str(key))
            if year_match:
                year = year_match.group(1)
                # 텍스트 정제
                cleaned_text = self.clean(value) if value else None
                if cleaned_text:
                    normalized[year] = cleaned_text
                    
        return normalized


def merge_yearly_opinions(opinions_dict: dict, separator: str = " ") -> str:
    """
    연도별 평가의견을 하나의 텍스트로 병합
    
    Args:
        opinions_dict: 연도별 평가의견 딕셔너리
        separator: 구분자
        
    Returns:
        병합된 텍스트
    """
    # 연도 순으로 정렬
    sorted_years = sorted(opinions_dict.keys())
    
    merged_parts = []
    for year in sorted_years:
        if opinions_dict[year]:
            # 연도 표시를 포함하여 병합
            merged_parts.append(f"[{year}년] {opinions_dict[year]}")
    
    return separator.join(merged_parts)


def calculate_text_statistics(text: str) -> dict:
    """
    텍스트 통계 계산
    
    Args:
        text: 분석할 텍스트
        
    Returns:
        통계 정보 딕셔너리
    """
    if not text:
        return {
            'char_count': 0,
            'word_count': 0,
            'sentence_count': 0,
            'avg_word_length': 0,
            'avg_sentence_length': 0
        }
    
    # 문자 수
    char_count = len(text)
    
    # 단어 수 (한국어와 영어 모두 고려)
    words = re.findall(r'\b\w+\b|[가-힣]+', text)
    word_count = len(words)
    
    # 문장 수
    sentences = re.split(r'[.!?。！？]+', text)
    sentences = [s for s in sentences if s.strip()]
    sentence_count = len(sentences)
    
    # 평균 계산
    avg_word_length = sum(len(w) for w in words) / word_count if word_count > 0 else 0
    avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
    
    return {
        'char_count': char_count,
        'word_count': word_count,
        'sentence_count': sentence_count,
        'avg_word_length': round(avg_word_length, 2),
        'avg_sentence_length': round(avg_sentence_length, 2)
    }