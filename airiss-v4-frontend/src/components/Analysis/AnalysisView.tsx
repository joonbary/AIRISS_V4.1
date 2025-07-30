import React, { useState, useEffect, useRef, useMemo } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import {
  Box,
  Paper,
  TextField,
  MenuItem,
  Button,
  Typography,
  Grid,
  LinearProgress,
  Alert,
  FormControl,
  InputLabel,
  Select,
  FormControlLabel,
  Switch,
  Chip,
  Card,
  CardContent,
  CircularProgress,
  SelectChangeEvent,
  AlertTitle,
  InputAdornment
} from '@mui/material';
import { PlayArrow, Stop, Download, Info, CheckCircle, Warning, Lock, PictureAsPdf } from '@mui/icons-material';
import { startAnalysis, getAnalysisStatus, downloadResults, checkResultsAvailability, getFiles, API_BASE_URL } from '../../services/api';
import { useWebSocket } from '../../hooks/useWebSocket';
import { AnalysisResult } from '../../types';
import axios from 'axios';

interface AnalysisViewProps {
  fileId?: string | null;
  fileName?: string;
  totalRecords?: number;
  columns?: string[];
  onAnalysisComplete?: (jobId: string) => void;
}

interface FileInfo {
  id: string;
  filename: string;
  upload_time: string;
  total_records: number;
  columns?: string[];
}

interface BackendWebSocketMessage {
  type: 'analysis_progress' | 'analysis_completed' | 'analysis_failed' | 'analysis_started' | 'alert';
  level?: string;
  message?: string;
  details?: any;
  progress?: number;
  current_uid?: string;
  processed?: number;
  total?: number;
  total_processed?: number;
  average_score?: number;
  error?: string;
}

const AnalysisView: React.FC<AnalysisViewProps> = ({
  fileId: propFileId,
  fileName: propFileName,
  totalRecords: propTotalRecords,
  columns: propColumns = [],
  onAnalysisComplete
}) => {
  // URL 파라미터 읽기
  const [searchParams] = useSearchParams();
  const urlFileId = searchParams.get('fileId');
  const urlFileName = searchParams.get('fileName');
  const urlTotalRecords = searchParams.get('totalRecords');
  const urlColumns = searchParams.get('columns');
  
  // 디버그 로그
  console.log('🔍 AnalysisView URL params:', {
    fileId: urlFileId,
    fileName: urlFileName,
    totalRecords: urlTotalRecords,
    columns: urlColumns
  });
  
  // localStorage에서 백업 데이터 확인
  const lastUploadedFile = localStorage.getItem('lastUploadedFile');
  let storageFileId = null;
  let storageFileName = null;
  let storageTotalRecords = null;
  let storageColumns = null;
  
  if (lastUploadedFile) {
    try {
      const parsed = JSON.parse(lastUploadedFile);
      storageFileId = parsed.fileId;
      storageFileName = parsed.fileName;
      storageTotalRecords = parsed.totalRecords;
      storageColumns = parsed.columns;
    } catch (e) {
      console.error('Failed to parse localStorage data:', e);
    }
  }
  
  // 우선순위: URL 파라미터 > localStorage > props
  const fileId = urlFileId || storageFileId || propFileId;
  const fileName = urlFileName || storageFileName || propFileName;
  const initialTotalRecords = urlTotalRecords ? parseInt(urlTotalRecords) : (storageTotalRecords || propTotalRecords);
  const initialColumns = urlColumns ? JSON.parse(decodeURIComponent(urlColumns)) : (storageColumns || propColumns);
  
  // 디버그 로그
  console.log('📊 AnalysisView initial values:', {
    fileId,
    fileName,
    initialTotalRecords,
    initialColumns: initialColumns?.length || 0
  });
  
  // 파일 목록 상태 추가
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [selectedFile, setSelectedFile] = useState<FileInfo | null>(null);
  const [isLoadingFiles, setIsLoadingFiles] = useState(true);

  // 기존 상태들
  const [currentFileId, setCurrentFileId] = useState<string | null>(fileId || null);
  const [currentFileName, setCurrentFileName] = useState<string>(fileName || '');
  const [totalRecords, setTotalRecords] = useState<number>(initialTotalRecords || 0);
  const [columns, setColumns] = useState<string[]>(initialColumns || []);
  
  // 작업 목록 상태 추가
  const [existingJobs, setExistingJobs] = useState<any[]>([]);
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);

  // 상태 관리
  const [sampleSize, setSampleSize] = useState<number>(25);
  const [analysisMode, setAnalysisMode] = useState<'text' | 'quantitative' | 'hybrid'>('hybrid');
  const [enableAI, setEnableAI] = useState(false);
  const [apiKey, setApiKey] = useState('');
  const [apiKeyConfigured, setApiKeyConfigured] = useState(false);
  const [maskedApiKey, setMaskedApiKey] = useState('');
  const [openaiModel, setOpenaiModel] = useState('gpt-3.5-turbo');
  const [maxTokens, setMaxTokens] = useState(1200);
  const [uidColumn, setUidColumn] = useState('');
  const [opinionColumn, setOpinionColumn] = useState('');
  const [quantColumns, setQuantColumns] = useState<string[]>([]);
  
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [jobId, setJobId] = useState<string | null>(null);
  const [currentProgress, setCurrentProgress] = useState(0);
  const [status, setStatus] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<AnalysisResult | null>(null);
  const [analysisCompleted, setAnalysisCompleted] = useState(false);
  const [downloadVisible, setDownloadVisible] = useState(false);

  // WebSocket 연결 (현재 폴링 전용 모드)
  const { 
    isConnected, 
    connect, 
    disconnect, 
    sendMessage,
    lastMessage,
    getJobProgress
  } = useWebSocket();
  
  // 강제 폴링 모드 (WebSocket 대신 폴링만 사용)
  const [forcePollMode, setForcePollMode] = useState(true);

  // 기존 작업 목록 가져오기
  useEffect(() => {
    const fetchExistingJobs = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/v1/analysis/jobs`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
        });
        
        if (response.ok) {
          const jobs = await response.json();
          const completedJobs = jobs.filter((job: any) => job.status === 'completed');
          setExistingJobs(completedJobs);
          
          // 가장 최근 완료된 작업 자동 선택
          if (completedJobs.length > 0 && !selectedJobId) {
            const latestJob = completedJobs[completedJobs.length - 1];
            setSelectedJobId(latestJob.id);
            setJobId(latestJob.id);
            
            // 분석 결과 표시
            if (latestJob.result && latestJob.result.analysis_results) {
              setResults(latestJob.result);
              setAnalysisCompleted(true);
              setCurrentProgress(100);
              setStatus('분석 완료!');
              setDownloadVisible(true);
              
              // 부모 컴포넌트에 jobId 전달
              if (onAnalysisComplete) {
                onAnalysisComplete(latestJob.id);
              }
            }
          }
        }
      } catch (error) {
        console.error('Failed to fetch existing jobs:', error);
      }
    };
    
    fetchExistingJobs();
  }, []);
  
  // 파일 목록 가져오기 (getFiles API 사용)
  useEffect(() => {
    const fetchFiles = async () => {
      try {
        // URL 파라미터로 fileId가 전달된 경우 (분석 서비스 업로드)
        if (fileId && fileName && !selectedFile) {
          console.log('🎯 Using file from URL parameters:', { fileId, fileName });
          // 가상의 파일 객체 생성
          const uploadedFile: FileInfo = {
            id: fileId,
            filename: fileName,
            upload_time: new Date().toISOString(),
            total_records: initialTotalRecords || propTotalRecords || 0,
            columns: initialColumns || propColumns || []
          };
          
          setFiles([uploadedFile]);
          setSelectedFile(uploadedFile);
          setCurrentFileId(uploadedFile.id);
          setCurrentFileName(uploadedFile.filename);
          setTotalRecords(initialTotalRecords || uploadedFile.total_records);
          setColumns(initialColumns || uploadedFile.columns || []);
          setIsLoadingFiles(false);
          return;
        }

        const data = await getFiles(); // data는 항상 배열
        setFiles(data);
        
        // fileId가 있으면 해당 파일 선택
        if (fileId && data.length > 0) {
          const targetFile = data.find((f: any) => f.id === fileId);
          if (targetFile) {
            setSelectedFile(targetFile);
            setCurrentFileId(targetFile.id);
            setCurrentFileName(targetFile.filename);
            setTotalRecords(targetFile.total_records);
            setColumns(targetFile.columns || []);
          }
        } 
        // fileId가 없고 propFileId도 없으면 가장 최근 파일 자동 선택
        else if (data.length > 0 && !propFileId) {
          const latestFile = data[0];
          setSelectedFile(latestFile);
          setCurrentFileId(latestFile.id);
          setCurrentFileName(latestFile.filename);
          setTotalRecords(latestFile.total_records);
          setColumns(latestFile.columns || []);
        }
      } catch (error: any) {
        console.error('Failed to fetch files:', error);
        setFiles([]);
        // 에러 타입에 따른 메시지 설정
        if (error.response?.status === 404) {
          setError('파일 목록 API를 찾을 수 없습니다. 백엔드 서버를 확인해주세요.');
        } else if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
          setError('서버 응답 시간이 초과되었습니다. 잠시 후 다시 시도해주세요.');
        } else if (!error.response) {
          setError('백엔드 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.');
        } else {
          setError('파일 목록을 불러오는 중 오류가 발생했습니다.');
        }
      } finally {
        setIsLoadingFiles(false);
      }
    };
    fetchFiles();
  }, [fileId, propFileId, fileName]);

  // 파일 선택 핸들러
  const handleFileSelect = (event: SelectChangeEvent<string>) => {
    const file = files.find(f => f.id === event.target.value);
    if (file) {
      setSelectedFile(file);
      setCurrentFileId(file.id);
      setCurrentFileName(file.filename);
      setTotalRecords(file.total_records);
      setColumns(file.columns || []);
    }
  };

  const validColumns = useMemo(() => Array.isArray(columns) ? columns : [], [columns]);

  // 컬럼 배열 검증
  // const validColumns = Array.isArray(columns) ? columns : []; // This line is now redundant as validColumns is moved

  // 컴포넌트 마운트 시 WebSocket 연결
  useEffect(() => {
    console.log('🔌 Attempting WebSocket connection...');
    connect(['analysis', 'alerts']);
    
    return () => {
      console.log('🔌 Disconnecting WebSocket...');
      disconnect();
    };
  }, []); // 빈 배열로 변경 - 컴포넌트 마운트 시에만 실행
  
  // 별도의 연결 상태 모니터링
  useEffect(() => {
    if (!isConnected && !isAnalyzing) {
      const reconnectTimer = setTimeout(() => {
        console.log('🔄 WebSocket disconnected, attempting to reconnect...');
        connect(['analysis', 'alerts']);
      }, 5000);
      
      return () => clearTimeout(reconnectTimer);
    }
  }, [isConnected, isAnalyzing]); // connect와 disconnect는 제외

  // UID와 Opinion 컬럼 자동 감지
  useEffect(() => {
    if (validColumns.length > 0 && !uidColumn) {
      // UID 컬럼 자동 감지
      const uidKeywords = ['uid', 'id', '아이디', '사번', '직원', 'user', 'emp'];
      const foundUid = validColumns.find(col => 
        uidKeywords.some(keyword => col.toLowerCase().includes(keyword))
      );
      if (foundUid) {
        setUidColumn(foundUid);
        console.log('🎯 Auto-detected UID column:', foundUid);
      }

      // Opinion 컬럼 자동 감지
      const opinionKeywords = ['의견', 'opinion', '평가', 'feedback', '내용', '코멘트', 'comment'];
      const foundOpinion = validColumns.find(col => 
        opinionKeywords.some(keyword => col.toLowerCase().includes(keyword))
      );
      if (foundOpinion) {
        setOpinionColumn(foundOpinion);
        console.log('🎯 Auto-detected Opinion column:', foundOpinion);
      }

      // 정량 컬럼 자동 감지
      const quantKeywords = ['점수', 'score', '평점', 'rating', '등급', 'grade'];
      const foundQuant = validColumns.filter(col => 
        quantKeywords.some(keyword => col.toLowerCase().includes(keyword))
      );
      if (foundQuant.length > 0) {
        setQuantColumns(foundQuant);
        console.log('🎯 Auto-detected Quantitative columns:', foundQuant);
      }
    }
  }, [validColumns, uidColumn]);

  // API 키 상태 확인
  useEffect(() => {
    const fetchApiKeyStatus = async () => {
      try {
        const response = await axios.get('/api/v1/config/api-key-status');
        if (response.data.configured) {
          setApiKeyConfigured(true);
          setMaskedApiKey(response.data.masked_key);
          console.log('✅ API 키가 환경변수에 설정되어 있습니다:', response.data.masked_key);
        } else {
          setApiKeyConfigured(false);
          console.log('⚠️ API 키가 환경변수에 설정되지 않았습니다');
        }
      } catch (error) {
        console.error('API 키 상태 확인 실패:', error);
        setApiKeyConfigured(false);
      }
    };

    fetchApiKeyStatus();
  }, []);

  // useWebSocket 훅의 메시지 처리
  useEffect(() => {
    if (lastMessage && jobId) {
      console.log('📡 WebSocket message:', lastMessage);
      
      switch (lastMessage.type) {
        case 'analysis_preparing':
          if (lastMessage.job_id === jobId) {
            setCurrentProgress(0);
            setStatus(lastMessage.message || '분석 준비 중...');
            setIsAnalyzing(true);
          }
          break;
          
        case 'analysis_progress':
          if (lastMessage.job_id === jobId) {
            const progressData = getJobProgress(jobId);
            if (progressData) {
              setCurrentProgress(progressData.progress);
              
              // 준비 단계인지 실제 분석 중인지 구분
              if (lastMessage.status === 'preparing' || progressData.progress < 10) {
                setStatus(lastMessage.message || '분석 준비 중...');
              } else {
                setStatus(`처리 중... ${progressData.current_uid || ''} (${progressData.processed || 0}/${progressData.total || totalRecords})`);
              }
            }
          }
          break;
          
        case 'analysis_completed':
          if (lastMessage.job_id === jobId) {
            setIsAnalyzing(false);
            setAnalysisCompleted(true);
            setCurrentProgress(100);
            setStatus('분석 완료!');
            
            // 완료 시 파일 존재 여부 확인 후 다운로드 버튼 활성화
            checkAndEnableDownload(jobId).catch(console.error);
            refreshAnalysisStatus(jobId);
            
            // 부모 컴포넌트에 분석 완료 알림
            console.log('🎉 분석 완료! jobId:', jobId, 'onAnalysisComplete 함수 존재:', !!onAnalysisComplete);
            if (onAnalysisComplete) {
              onAnalysisComplete(jobId);
            }
          }
          break;
          
        case 'analysis_failed':
          if (lastMessage.job_id === jobId) {
            setError(lastMessage.error || '분석 실패');
            setIsAnalyzing(false);
            setStatus('분석 실패');
            setCurrentProgress(0);
          }
          break;
          
        case 'alert':
          // alert 타입의 메시지 처리
          if (lastMessage.level === 'success' && lastMessage.message?.includes('Analysis completed')) {
            const completedJobId = lastMessage.data?.job_id || jobId;
            if (completedJobId === jobId) {
              setIsAnalyzing(false);
              setAnalysisCompleted(true);
              setCurrentProgress(100);
              setStatus('분석 완료!');
              
              checkAndEnableDownload(jobId).catch(console.error);
              refreshAnalysisStatus(jobId);
              
              // 부모 컴포넌트에 분석 완료 알림
              console.log('🎉 분석 완료 (alert)! completedJobId:', completedJobId, 'onAnalysisComplete 함수 옆재:', !!onAnalysisComplete);
              if (onAnalysisComplete) {
                onAnalysisComplete(completedJobId);
              }
            }
          } else if (lastMessage.level === 'error') {
            setError(lastMessage.message || '오류 발생');
            setIsAnalyzing(false);
            setStatus('분석 실패');
          }
          break;
      }
    }
  }, [lastMessage, jobId, totalRecords, getJobProgress]);

  // 파일 존재 여부 확인 및 다운로드 버튼 활성화
  const checkAndEnableDownload = async (jobId: string) => {
    try {
      console.log('🔍 Checking file availability for job:', jobId);
      const availability = await checkResultsAvailability(jobId);
      console.log('📄 File availability check result:', availability);
      
      if (availability.available) {
        setDownloadVisible(true);
        console.log('✅ Download buttons enabled - files are available');
        console.log('📊 Available formats:', availability.formats);
        console.log('📈 Record count:', availability.record_count);
      } else {
        console.warn('⚠️ Files not available:', availability.reason);
        setDownloadVisible(false);
      }
    } catch (error) {
      console.error('❌ File availability check failed:', error);
      setDownloadVisible(false);
    }
  };

  // 분석 상태 새로고침
  const refreshAnalysisStatus = async (jobId: string) => {
    try {
      const statusData = await getAnalysisStatus(jobId);
      console.log('🔄 Status refresh:', statusData);
      
      // 분석 완료 상태 확인
      if (statusData.status === 'completed') {
        console.log('🎯 분석 완료 감지! statusData:', statusData);
        setAnalysisCompleted(true);
        setCurrentProgress(100);
        setStatus('분석 완료!');
        
        // 파일 존재 여부 확인 후 다운로드 버튼 활성화
        await checkAndEnableDownload(jobId);
        
        console.log('📌 다운로드 버튼 상태:', {
          downloadVisible: true,
          analysisCompleted: true,
          jobId: jobId
        });
      }
      
      if (statusData.average_score !== undefined) {
        setResults({
          total_analyzed: statusData.processed || statusData.total || totalRecords,
          average_score: statusData.average_score,
          processing_time: statusData.processing_time || '완료'
        } as AnalysisResult);
      }
    } catch (err) {
      console.error('❌ Status refresh failed:', err);
    }
  };

  // 분석 상태 폴링 (강제 폴링 모드 또는 WebSocket 실패 시)
  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (jobId && isAnalyzing) {
      console.log('🔄 Starting status polling for job:', jobId);
      
      interval = setInterval(async () => {
        try {
          const statusData = await getAnalysisStatus(jobId);
          console.log('📊 Polling status:', statusData);
          
          // 폴링: WebSocket 불안정 시에도 진행률 및 완료상태 감지
          console.log('📊 Polling status update:', statusData);
          
          // 강제 폴링 모드이거나 WebSocket이 연결되지 않았으면 폴링으로 업데이트
          if (forcePollMode || !isConnected) {
            console.log('🔄 Updating via polling (Force polling mode or WebSocket disconnected)');
            setCurrentProgress(statusData.progress || 0);
            setStatus(`처리 중... (${statusData.processed || 0}/${statusData.total || totalRecords})`);
          }
          
          // 분석 완료는 WebSocket 상태와 관계없이 항상 확인
          if (statusData.status === 'completed') {
            console.log('🎯 Analysis completed detected via polling!', statusData);
            setIsAnalyzing(false);
            setAnalysisCompleted(true);
            setCurrentProgress(100);
            setStatus('분석 완료!');
            clearInterval(interval);
            
            // 파일 존재 여부 확인 후 다운로드 버튼 활성화
            await checkAndEnableDownload(jobId);
            
            // 결과 설정
            if (statusData.average_score !== undefined) {
              setResults({
                total_analyzed: statusData.processed || totalRecords,
                average_score: statusData.average_score,
                processing_time: statusData.processing_time || '완료'
              } as AnalysisResult);
            }
          } else if (statusData.status === 'failed') {
            setError(statusData.error || '분석 실패');
            setIsAnalyzing(false);
            setCurrentProgress(0);
            clearInterval(interval);
          }
        } catch (err) {
          console.error('❌ Polling error:', err);
        }
      }, forcePollMode ? 1500 : (isConnected ? 5000 : 2000)); // 강제 폴링 모드: 1.5초, 기타: 기존 로직

      return () => clearInterval(interval);
    }
  }, [jobId, isAnalyzing, totalRecords, isConnected]);

  // WebSocket 메시지 처리 (강제 폴링 모드에서는 비활성화)
  useEffect(() => {
    if (!lastMessage || forcePollMode) return;
    
    console.log('📨 WebSocket message received:', lastMessage);
    
    const handleWebSocketMessage = async () => {
      // 분석 진행 상황 업데이트
      if (lastMessage.type === 'analysis_progress' && lastMessage.job_id === jobId) {
        console.log('📊 Progress update:', lastMessage);
        setCurrentProgress(lastMessage.progress || 0);
        setStatus(`처리 중... (${lastMessage.processed || 0}/${lastMessage.total || totalRecords})`);
        
        // 평균 점수가 있으면 결과 업데이트
        if (lastMessage.average_score !== undefined) {
          setResults({
            total_analyzed: lastMessage.processed || 0,
            average_score: lastMessage.average_score,
            processing_time: '진행 중...'
          } as AnalysisResult);
        }
      }
      
      // 분석 완료 처리
      if (lastMessage.type === 'analysis_completed' && lastMessage.job_id === jobId) {
        console.log('🎯 Analysis completed via WebSocket!', lastMessage);
        setIsAnalyzing(false);
        setAnalysisCompleted(true);
        setCurrentProgress(100);
        setStatus('분석 완료!');
        
        // 결과 설정
        if (lastMessage.average_score !== undefined) {  
          setResults({
            total_analyzed: lastMessage.total_processed || totalRecords,
            average_score: lastMessage.average_score,
            processing_time: '완료'
          } as AnalysisResult);
        }
        
        // 파일 존재 여부 확인 후 다운로드 버튼 활성화
        if (jobId) {
          await checkAndEnableDownload(jobId);
        }
      }
      
      // 분석 실패 처리
      if (lastMessage.type === 'analysis_failed' && lastMessage.job_id === jobId) {
        console.log('❌ Analysis failed via WebSocket:', lastMessage);
        setIsAnalyzing(false);
        setCurrentProgress(0);
        setError(lastMessage.error || '분석 실패');
      }
    };

    handleWebSocketMessage();
  }, [lastMessage, jobId, totalRecords]);

  // 분석 시작
  const handleStartAnalysis = async () => {
    console.log('🎯 handleStartAnalysis called');
    console.log('Current state:', {
      currentFileId,
      selectedFile,
      totalRecords,
      columns: columns?.length || 0,
      sampleSize,
      analysisMode
    });

    if (!currentFileId) {
      setError('파일을 먼저 선택해주세요.');
      return;
    }

    // Validate file has records
    if (totalRecords === 0) {
      setError('파일에 데이터가 없습니다. 다른 파일을 선택해주세요.');
      console.error('❌ Cannot analyze file with 0 records');
      return;
    }

    // 상태 초기화
    setError(null);
    setIsAnalyzing(true);
    setAnalysisCompleted(false);
    setCurrentProgress(0);
    setDownloadVisible(false);  // 다운로드 버튼 숨기기
    setStatus('분석 시작 중...');
    setResults(null);

    try {
      // 강제 폴링 모드에서는 WebSocket 연결 시도하지 않음
      if (!forcePollMode && !isConnected) {
        console.log('🔌 Connecting to WebSocket...');
        try {
          await connect(['analysis', 'alerts']);
          await new Promise(resolve => setTimeout(resolve, 1000));
        } catch (wsError) {
          console.warn('⚠️ WebSocket connection failed, using polling mode:', wsError);
        }
      }

      // 백엔드 요청 파라미터 (AnalysisRequest 모델과 완벽히 일치)
      const requestParams = {
        file_id: currentFileId,
        sample_size: sampleSize,
        analysis_mode: analysisMode,
        enable_ai_feedback: enableAI,
        // API 키가 환경변수에 설정되어 있으면 전송하지 않음
        openai_api_key: enableAI && !apiKeyConfigured ? apiKey : undefined,
        openai_model: openaiModel,
        max_tokens: maxTokens
      };

      console.log('🚀 Starting analysis:', requestParams);
      console.log('📊 Expected to analyze:', Math.min(sampleSize, totalRecords), 'records out of', totalRecords);

      const response = await startAnalysis(requestParams);
      console.log('✅ Analysis started:', response);
      
      setJobId(response.job_id);
      setStatus(response.message || '분석이 시작되었습니다');
      console.log('🎯 분석 시작됨. jobId:', response.job_id);
      
      // 분석 시작 시 부모 컴포넌트에 jobId 전달
      if (onAnalysisComplete) {
        console.log('🚀 분석 시작 시 부모에게 jobId 전달:', response.job_id);
        onAnalysisComplete(response.job_id);
      }
      
      // WebSocket 메시지 전송 (분석 구독)
      if (isConnected && sendMessage) {
        const subscribeSuccess = sendMessage({
          type: 'subscribe',
          channels: ['analysis'],
          job_id: response.job_id
        });
        console.log('📡 Subscribe to analysis channel:', subscribeSuccess);
      } else {
        console.warn('⚠️ WebSocket not connected, will rely on polling');
      }
    } catch (err: any) {
      console.error('❌ Analysis start failed:', err);
      
      let errorMessage = '분석 시작 실패';
      if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
      setIsAnalyzing(false);
      setAnalysisCompleted(false);
    }
  };

  // 결과 다운로드
  const handleDownload = async (format: string = 'excel') => {
    if (!jobId) {
      setError('다운로드할 분석 결과가 없습니다.');
      return;
    }

    try {
      console.log(`📥 Downloading: /analysis/download/${jobId}/${format}`);
      
      const blob = await downloadResults(jobId, format);
      
      // 파일 확장자 및 MIME 타입 설정
      let extension = 'xlsx';
      let mimeType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
      
      if (format === 'csv') {
        extension = 'csv';
        mimeType = 'text/csv;charset=utf-8;';
      } else if (format === 'json') {
        extension = 'json';
        mimeType = 'application/json;charset=utf-8;';
      }
      
      // 다운로드 실행
      const url = window.URL.createObjectURL(new Blob([blob], { type: mimeType }));
      const link = document.createElement('a');
      link.href = url;
      link.download = `AIRISS_v4_분석결과_${new Date().toISOString().split('T')[0]}.${extension}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      console.log('✅ Download completed');
    } catch (err: any) {
      console.error('❌ Download failed:', err);
      setError(`다운로드 실패: ${err.message || '알 수 없는 오류'}`);
    }
  };

  // 개인별 PDF 다운로드
  const handlePdfDownload = async (employeeId: string, employeeName: string = '') => {
    if (!jobId) {
      setError('다운로드할 분석 결과가 없습니다.');
      return;
    }

    try {
      console.log('📄 AnalysisView PDF 다운로드:', { 
        employeeId: employeeId, 
        employeeIdType: typeof employeeId,
        employeeIdLength: employeeId.length,
        containsDtype: employeeId.includes('dtype'),
        callStack: new Error().stack
      });
      
      const response = await fetch(`${API_BASE_URL}/api/v1/analysis/pdf/${jobId}/${employeeId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const blob = await response.blob();
      
      // 다운로드 실행
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `AIRISS_v4_${employeeId}_${employeeName}_리포트.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      console.log('✅ PDF Download completed');
    } catch (err: any) {
      console.error('❌ PDF Download failed:', err);
      setError(`PDF 다운로드 실패: ${err.message || '알 수 없는 오류'}`);
    }
  };

  // Select 핸들러
  const handleSampleSizeChange = (event: SelectChangeEvent<number>) => {
    setSampleSize(event.target.value as number);
  };

  const handleAnalysisModeChange = (event: SelectChangeEvent<string>) => {
    setAnalysisMode(event.target.value as 'text' | 'quantitative' | 'hybrid');
  };

  const handleModelChange = (event: SelectChangeEvent<string>) => {
    setOpenaiModel(event.target.value);
  };

  const handleMaxTokensChange = (event: SelectChangeEvent<number>) => {
    setMaxTokens(event.target.value as number);
  };

  return (
    <Box>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" gutterBottom>
          AIRISS v4.0 분석 설정
        </Typography>
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            <AlertTitle>오류</AlertTitle>
            {error}
          </Alert>
        )}

        <Grid container spacing={3}>
          {/* 기존 분석 결과 */}
          {existingJobs.length > 0 && (
            <Grid item xs={12}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    기존 분석 결과
                  </Typography>
                  <FormControl fullWidth sx={{ mb: 2 }}>
                    <Select
                      value={selectedJobId || ''}
                      onChange={(e) => {
                        const jobId = e.target.value;
                        setSelectedJobId(jobId);
                        setJobId(jobId);
                        
                        // 선택된 작업의 결과 표시
                        const job = existingJobs.find(j => j.id === jobId);
                        if (job && job.result) {
                          setResults(job.result);
                          setAnalysisCompleted(true);
                          setCurrentProgress(100);
                          setStatus('분석 완료!');
                          setDownloadVisible(true);
                          
                          // 파일 정보 업데이트
                          if (job.file_id) {
                            setCurrentFileId(job.file_id);
                            setCurrentFileName(job.filename || '');
                          }
                          
                          // 부모 컴포넌트에 jobId 전달
                          if (onAnalysisComplete) {
                            onAnalysisComplete(jobId);
                          }
                        }
                      }}
                      displayEmpty
                    >
                      <MenuItem value="" disabled>
                        분석 결과를 선택하세요
                      </MenuItem>
                      {existingJobs.map((job) => (
                        <MenuItem key={job.id} value={job.id}>
                          {job.filename || '알 수 없는 파일'} - {new Date(job.created_at).toLocaleString('ko-KR')}
                          {job.result?.analysis_results && ` (${job.result.analysis_results.length}명 분석)`}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  {selectedJobId && results && (
                    <Alert severity="success" sx={{ mt: 2 }}>
                      <AlertTitle>분석 완료</AlertTitle>
                      {results.analysis_results?.length || 0}명의 직원 분석 완료
                    </Alert>
                  )}
                </CardContent>
              </Card>
            </Grid>
          )}
          
          {/* 파일 정보 */}
          <Grid item xs={12}>
            <Card variant="outlined">
              <CardContent>
                {isLoadingFiles ? (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <CircularProgress size={20} />
                    <Typography>파일 목록을 불러오는 중...</Typography>
                  </Box>
                ) : error ? (
                  <Alert severity="error">
                    <AlertTitle>오류 발생</AlertTitle>
                    {error}
                    <Box sx={{ mt: 2 }}>
                      <Button 
                        variant="contained" 
                        size="small" 
                        onClick={() => window.location.reload()}
                      >
                        페이지 새로고침
                      </Button>
                    </Box>
                  </Alert>
                ) : files.length === 0 ? (
                  <Alert severity="warning">
                    <AlertTitle>파일 없음</AlertTitle>
                    먼저 파일을 업로드해주세요.
                    <Box sx={{ mt: 2 }}>
                      <Button 
                        variant="contained" 
                        size="small" 
                        component={Link} 
                        to="/upload"
                      >
                        파일 업로드하기
                      </Button>
                    </Box>
                  </Alert>
                ) : (
                  <>
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                      분석 대상 파일
                    </Typography>
                    <FormControl fullWidth sx={{ mb: 2 }}>
                      <Select
                        value={currentFileId || ''}
                        onChange={handleFileSelect}
                        displayEmpty
                      >
                        <MenuItem value="" disabled>
                          파일을 선택하세요
                        </MenuItem>
                        {files.map((file) => (
                          <MenuItem key={file.id} value={file.id}>
                            {file.filename} ({file.total_records}개 레코드)
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                    {selectedFile && (
                      <>
                        <Typography variant="h6">{currentFileName}</Typography>
                        <Typography variant="body2" color="text.secondary">
                          총 {(totalRecords || 0).toLocaleString()}개 레코드
                        </Typography>
                        {columns.length > 0 && (
                          <Typography variant="body2" color="text.secondary">
                            {columns.length}개 컬럼 감지됨
                          </Typography>
                        )}
                      </>
                    )}
                  </>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* 자동 감지된 컬럼 정보 표시 */}
          {validColumns.length > 0 && (
            <Grid item xs={12}>
              <Alert severity="info" icon={<Info />}>
                <AlertTitle>자동 감지된 컬럼 정보</AlertTitle>
                <Box sx={{ mt: 1 }}>
                  {uidColumn && (
                    <Typography variant="body2">
                      • UID 컬럼: <strong>{uidColumn}</strong>
                    </Typography>
                  )}
                  {opinionColumn && (
                    <Typography variant="body2">
                      • 의견 컬럼: <strong>{opinionColumn}</strong>
                    </Typography>
                  )}
                  {quantColumns.length > 0 && (
                    <Typography variant="body2">
                      • 정량 데이터 컬럼: <strong>{quantColumns.join(', ')}</strong>
                    </Typography>
                  )}
                  {!uidColumn && !opinionColumn && (
                    <Typography variant="body2" color="warning.main">
                      ⚠️ UID 또는 의견 컬럼을 자동으로 감지하지 못했습니다. 
                      백엔드에서 기본 컬럼 탐지를 수행합니다.
                    </Typography>
                  )}
                </Box>
              </Alert>
            </Grid>
          )}

          {/* 분석 설정 */}
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>샘플 크기</InputLabel>
              <Select value={sampleSize} onChange={handleSampleSizeChange}>
                <MenuItem value={10}>10개 (테스트)</MenuItem>
                <MenuItem value={25}>25개 (표준)</MenuItem>
                <MenuItem value={50}>50개 (상세)</MenuItem>
                <MenuItem value={100}>100개 (정밀)</MenuItem>
                <MenuItem value={totalRecords || 0}>전체 데이터 ({(totalRecords || 0).toLocaleString()}개)</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>분석 모드</InputLabel>
              <Select value={analysisMode} onChange={handleAnalysisModeChange}>
                <MenuItem value="text">텍스트 분석</MenuItem>
                <MenuItem value="quantitative">정량 분석</MenuItem>
                <MenuItem value="hybrid">하이브리드 (추천)</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          {/* AI 설정 */}
          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={enableAI}
                  onChange={(e) => setEnableAI(e.target.checked)}
                />
              }
              label="OpenAI GPT 피드백 활성화 (선택사항)"
            />
          </Grid>

          {enableAI && (
            <>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  type="password"
                  label="OpenAI API Key"
                  value={apiKeyConfigured ? maskedApiKey : apiKey}
                  onChange={(e) => !apiKeyConfigured && setApiKey(e.target.value)}
                  placeholder={apiKeyConfigured ? "환경변수에 설정됨" : "sk-..."}
                  disabled={apiKeyConfigured}
                  InputProps={{
                    startAdornment: apiKeyConfigured ? (
                      <InputAdornment position="start">
                        <Lock color="success" fontSize="small" />
                      </InputAdornment>
                    ) : undefined,
                  }}
                  helperText={apiKeyConfigured ? "API 키가 안전하게 서버에 설정되어 있습니다" : ""}
                />
              </Grid>
              
              <Grid item xs={12} md={4}>
                <FormControl fullWidth>
                  <InputLabel>모델 선택</InputLabel>
                  <Select value={openaiModel} onChange={handleModelChange}>
                    <MenuItem value="gpt-3.5-turbo">GPT-3.5 Turbo</MenuItem>
                    <MenuItem value="gpt-4">GPT-4</MenuItem>
                    <MenuItem value="gpt-4-turbo">GPT-4 Turbo</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} md={4}>
                <FormControl fullWidth>
                  <InputLabel>응답 길이</InputLabel>
                  <Select value={maxTokens} onChange={handleMaxTokensChange}>
                    <MenuItem value={800}>간단 (800 토큰)</MenuItem>
                    <MenuItem value={1200}>표준 (1200 토큰)</MenuItem>
                    <MenuItem value={1500}>상세 (1500 토큰)</MenuItem>
                    <MenuItem value={2000}>완전 (2000 토큰)</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </>
          )}

          {/* 분석 버튼 */}
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
              <Button
                variant="contained"
                size="large"
                startIcon={isAnalyzing ? <Stop /> : <PlayArrow />}
                onClick={handleStartAnalysis}
                disabled={isAnalyzing || !currentFileId}
                sx={{
                  bgcolor: '#FF5722',
                  '&:hover': { bgcolor: '#E64A19' }
                }}
              >
                {isAnalyzing ? '분석 중...' : '분석 시작'}
              </Button>
              
              {isConnected ? (
                <Chip
                  label="실시간 연결됨"
                  color="success"
                  size="small"
                  icon={<CheckCircle />}
                />
              ) : (
                <Chip
                  label="폴링 모드"
                  color="warning"
                  size="small"
                  icon={<Warning />}
                />
              )}
              
              {jobId && (
                <Typography variant="caption" color="text.secondary">
                  작업 ID: {jobId.substring(0, 8)}...
                </Typography>
              )}
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* 진행 상황 */}
      {(isAnalyzing || currentProgress > 0) && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            분석 진행 상황
          </Typography>
          <Box sx={{ mb: 2 }}>
            <LinearProgress 
              variant="determinate" 
              value={currentProgress} 
              sx={{ 
                height: 10, 
                borderRadius: 5,
                bgcolor: 'grey.300',
                '& .MuiLinearProgress-bar': {
                  bgcolor: '#FF5722'
                }
              }}
            />
          </Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              {status || '처리 중...'} - {(currentProgress || 0).toFixed(0)}% 완료
              {forcePollMode && <span style={{ color: '#2196F3', marginLeft: '8px' }}>(폴링 모드)</span>}
            </Typography>
            {jobId && (
              <Button
                size="small"
                variant="outlined"
                onClick={() => jobId && refreshAnalysisStatus(jobId)}
                disabled={!jobId}
                sx={{ ml: 2 }}
              >
                상태 새로고침
              </Button>
            )}
          </Box>
        </Paper>
      )}

      {/* 결과 */}
      {results && analysisCompleted && (
        <Paper sx={{ p: 3 }}>
          <>
            <Typography variant="h6" gutterBottom>
              분석 완료
            </Typography>
            <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={4}>
              <Card>
                <CardContent>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    총 분석
                  </Typography>
                  <Typography variant="h4" color="primary">
                    {results.total_analyzed}개
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Card>
                <CardContent>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    평균 점수
                  </Typography>
                  <Typography variant="h4" color="primary">
                    {results.average_score?.toFixed(1)}점
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Card>
                <CardContent>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    소요 시간
                  </Typography>
                  <Typography variant="h4" color="primary">
                    {results.processing_time}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
          
          {/* 분석 결과 상세 보기 */}
          {results && results.analysis_results && results.analysis_results.length > 0 && (
            <Box sx={{ mt: 3 }}>
              <Typography variant="h6" gutterBottom>
                직원별 분석 결과
              </Typography>
              <Box sx={{ maxHeight: 400, overflowY: 'auto' }}>
                {results.analysis_results.map((result: any, index: number) => (
                  <Card key={index} sx={{ mb: 2 }}>
                    <CardContent>
                      <Grid container spacing={2}>
                        <Grid item xs={12} sm={5}>
                          <Typography variant="subtitle1" fontWeight="bold">
                            {result.name || result.employee_id || result.uid || `직원 ${index + 1}`}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            최종 점수: <strong>{result.final_score?.toFixed(1) || 'N/A'}점</strong>
                          </Typography>
                        </Grid>
                        <Grid item xs={12} sm={5}>
                          {result.qualitative_scores && (
                            <>
                              <Typography variant="body2">
                                정성 점수: {result.qualitative_scores.sentiment?.toFixed(1) || 'N/A'}
                              </Typography>
                              <Typography variant="body2">
                                키워드 점수: {result.qualitative_scores.keyword?.toFixed(1) || 'N/A'}
                              </Typography>
                            </>
                          )}
                        </Grid>
                        <Grid item xs={12} sm={2}>
                          <Button
                            variant="outlined"
                            size="small"
                            startIcon={<PictureAsPdf />}
                            onClick={() => handlePdfDownload(
                              result.employee_id || result.uid || `employee_${index + 1}`,
                              result.name || ''
                            )}
                            sx={{
                              color: '#FF5722',
                              borderColor: '#FF5722',
                              '&:hover': { 
                                borderColor: '#E64A19',
                                bgcolor: 'rgba(255, 87, 34, 0.08)'
                              }
                            }}
                          >
                            PDF
                          </Button>
                        </Grid>
                        {result.top_keywords && result.top_keywords.length > 0 && (
                          <Grid item xs={12}>
                            <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mt: 1 }}>
                              <Typography variant="body2" color="text.secondary">주요 키워드:</Typography>
                              {result.top_keywords.map((kw: any, idx: number) => (
                                <Chip
                                  key={idx}
                                  label={`${kw.keyword} (${kw.count})`}
                                  size="small"
                                  variant="outlined"
                                />
                              ))}
                            </Box>
                          </Grid>
                        )}
                      </Grid>
                    </CardContent>
                  </Card>
                ))}
              </Box>
            </Box>
          )}
          
          {console.log('🔍 다운로드 버튼 렌더링 체크:', {
            downloadVisible,
            analysisCompleted,
            jobId,
            조건결과: (downloadVisible || analysisCompleted) && jobId
          })}
          {(downloadVisible || analysisCompleted) && jobId && (
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              <Button
                variant="contained"
                startIcon={<Download />}
                onClick={() => handleDownload('excel')}
                disabled={!jobId}
                sx={{
                  bgcolor: '#FF5722',
                  '&:hover': { bgcolor: '#E64A19' }
                }}
              >
                Excel 다운로드
              </Button>
              <Button
                variant="outlined"
                startIcon={<Download />}
                onClick={() => handleDownload('csv')}
                disabled={!jobId}
                sx={{
                  color: '#FF5722',
                  borderColor: '#FF5722',
                  '&:hover': { 
                    borderColor: '#E64A19',
                    bgcolor: 'rgba(255, 87, 34, 0.08)'
                  }
                }}
              >
                CSV 다운로드
              </Button>
              <Button
                variant="outlined"
                startIcon={<Download />}
                onClick={() => handleDownload('json')}
                disabled={!jobId}
              sx={{
                color: '#FF5722',
                borderColor: '#FF5722',
                '&:hover': { 
                  borderColor: '#E64A19',
                  bgcolor: 'rgba(255, 87, 34, 0.08)'
                }
              }}
            >
              JSON 다운로드
            </Button>
            </Box>
          )}
          </>
        </Paper>
      )}
    </Box>
  );
}

export default AnalysisView;