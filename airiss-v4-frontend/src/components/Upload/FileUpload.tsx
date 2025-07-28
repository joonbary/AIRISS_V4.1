import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Paper,
  Typography,
  Button,
  LinearProgress,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip
} from '@mui/material';
import {
  CloudUpload,
  InsertDriveFile,
  CheckCircle,
  Error as ErrorIcon
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import { uploadFile } from '../../services/api';
import { FileUploadResponse } from '../../types';
import DashboardLayout from '../Layout/DashboardLayout';

interface FileUploadProps {
  onUploadSuccess?: (data: {
    fileId: string;
    fileName: string;
    totalRecords: number;
    columns: string[];
  }) => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onUploadSuccess }) => {
  const navigate = useNavigate();
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [fileInfo, setFileInfo] = useState<FileUploadResponse | null>(null);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles?.length === 0) return;

    const file = acceptedFiles[0];
    
    // 파일 크기 검증 (100MB)
    if (file.size > 100 * 1024 * 1024) {
      setError('파일 크기는 100MB를 초과할 수 없습니다.');
      return;
    }

    // 파일 타입 검증
    const validTypes = [
      'text/csv',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ];
    
    if (!validTypes.includes(file.type) && !file.name.match(/\.(csv|xls|xlsx)$/)) {
      setError('CSV 또는 Excel 파일만 업로드 가능합니다.');
      return;
    }

    console.log('📁 File selected for upload:', {
      name: file.name,
      size: file.size,
      type: file.type,
      lastModified: new Date(file.lastModified).toISOString()
    });

    setError(null);
    setUploadStatus('uploading');
    setUploadProgress(0);

    // 진행률 시뮬레이션
    const progressInterval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 90) {
          clearInterval(progressInterval);
          return prev;
        }
        return prev + 10;
      });
    }, 200);

    try {
      const response = await uploadFile(file);
      console.log('📡 Upload Response:', response);
      
      // Validate response
      if (response.total_records === 0) {
        console.warn('⚠️ File has 0 records!');
        setError('경고: 파일에 데이터가 없습니다 (0개 레코드)');
      } else {
        console.log('✅ File has', response.total_records, 'records');
      }
      
      setFileInfo(response);
      setUploadProgress(100);
      setUploadStatus('success');
      
      if (onUploadSuccess) {
        // 백엔드에서 받은 columns를 직접 사용
        console.log('📤 Columns from backend:', response.columns);
        console.log('📤 Column count:', response.columns?.length || 0);
        console.log('📊 Total records:', response.total_records);
        
        onUploadSuccess({
          fileId: response.file_id,
          fileName: response.filename,
          totalRecords: response.total_records,
          columns: response.columns || [] // 백엔드에서 받은 columns 직접 사용
        });
      }
      
      // localStorage에도 저장 (백업)
      localStorage.setItem('lastUploadedFile', JSON.stringify({
        fileId: response.file_id,
        fileName: response.filename,
        totalRecords: response.total_records,
        columns: response.columns || [],
        uploadTime: new Date().toISOString()
      }));
      
      // 업로드 성공 후 분석 화면으로 이동
      const analysisUrl = `/analysis?fileId=${response.file_id}&fileName=${encodeURIComponent(response.filename || 'uploaded_file')}&totalRecords=${response.total_records}&columns=${encodeURIComponent(JSON.stringify(response.columns || []))}`;
      console.log('🚀 Redirecting to:', analysisUrl);
      
      setTimeout(() => {
        navigate(analysisUrl);
      }, 1500); // 1.5초 후 이동 (성공 메시지를 볼 수 있도록)
    } catch (err: any) {
      console.error('Upload error:', err);
      setError(err.response?.data?.detail || '파일 업로드 실패');
      setUploadStatus('error');
    } finally {
      clearInterval(progressInterval);
    }
  }, [onUploadSuccess, navigate]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx']
    },
    multiple: false
  });

  // 파일 크기 포맷 함수
  const formatFileSize = (bytes?: number) => {
    if (!bytes || typeof bytes !== 'number') return '0 KB';
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)).toString());
    return Math.round((bytes / Math.pow(1024, i)) * 100) / 100 + ' ' + sizes[i];
  };

  // 날짜 포맷 함수
  const formatDate = (date?: string | number) => {
    if (!date) return '-';
    try {
      return new Date(date).toLocaleString();
    } catch (error) {
      return '-';
    }
  };

  let content: React.ReactNode;
  try {
    content = (
      <DashboardLayout>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h5" gutterBottom>
            파일 업로드
          </Typography>

          <Box
            {...getRootProps()}
            sx={{
              border: '2px dashed',
              borderColor: isDragActive ? 'primary.main' : 'grey.300',
              borderRadius: 2,
              p: 4,
              mt: 2,
              mb: 2,
              textAlign: 'center',
              cursor: 'pointer',
              backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
              transition: 'all 0.3s ease'
            }}
          >
            <input {...getInputProps()} />
            <CloudUpload sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              {isDragActive ? '파일을 놓으세요' : '파일을 드래그하거나 클릭하여 선택'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              CSV, Excel (XLS, XLSX) 파일 지원 (최대 100MB)
            </Typography>
          </Box>

          {uploadStatus === 'uploading' && (
            <Box sx={{ mb: 2 }}>
              <LinearProgress variant="determinate" value={uploadProgress} />
              <Typography variant="body2" sx={{ mt: 1 }}>
                업로드 중... {uploadProgress}%
              </Typography>
            </Box>
          )}

          {error && (
            <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          {fileInfo && uploadStatus === 'success' && (
            <Alert severity="success" sx={{ mb: 2 }}>
              파일 업로드 완료! 잠시 후 분석 페이지로 이동합니다...
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2">
                  <strong>파일명:</strong> {fileInfo.filename || 'Unknown'}
                </Typography>
                <Typography variant="body2">
                  <strong>레코드 수:</strong> {typeof fileInfo.total_records === 'number' ? fileInfo.total_records.toLocaleString() : (fileInfo.total_records || 0)}개
                </Typography>
                <Typography variant="body2">
                  <strong>컬럼 수:</strong> {fileInfo.columns?.length ?? 0}개
                </Typography>
                {/* 파일 크기 및 날짜(옵션) 안전 표시 */}
                {'file_size' in fileInfo && (
                  <Typography variant="body2">
                    <strong>파일 크기:</strong> {formatFileSize((fileInfo as any).file_size)}
                  </Typography>
                )}
                {'upload_time' in fileInfo && (
                  <Typography variant="body2">
                    <strong>업로드 시간:</strong> {formatDate((fileInfo as any).upload_time)}
                  </Typography>
                )}
                <Box sx={{ mt: 1 }}>
                  {fileInfo.uid_columns && fileInfo.uid_columns.length > 0 && (
                    <Chip
                      label={`UID 컬럼: ${fileInfo.uid_columns?.join(', ')}`}
                      size="small"
                      color="primary"
                      sx={{ mr: 1 }}
                    />
                  )}
                  {fileInfo.opinion_columns && fileInfo.opinion_columns.length > 0 && (
                    <Chip
                      label={`의견 컬럼: ${fileInfo.opinion_columns?.join(', ')}`}
                      size="small"
                      color="secondary"
                      sx={{ mr: 1 }}
                    />
                  )}
                  {fileInfo.quantitative_columns && fileInfo.quantitative_columns.length > 0 && (
                    <Chip
                      label={`정량 컬럼: ${fileInfo.quantitative_columns?.length || 0}개`}
                      size="small"
                      color="success"
                    />
                  )}
                </Box>
                <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
                  <Button 
                    variant="contained" 
                    size="small" 
                    onClick={() => navigate(`/analysis?fileId=${fileInfo.file_id}&fileName=${encodeURIComponent(fileInfo.filename)}&totalRecords=${fileInfo.total_records}&columns=${encodeURIComponent(JSON.stringify(fileInfo.columns || []))}`)}
                  >
                    지금 분석하기
                  </Button>
                  <Button 
                    variant="outlined" 
                    size="small" 
                    onClick={() => {
                      setFileInfo(null);
                      setUploadStatus('idle');
                    }}
                  >
                    다른 파일 업로드
                  </Button>
                </Box>
              </Box>
            </Alert>
          )}

          <Typography variant="h6" sx={{ mt: 3, mb: 2 }}>
            지원되는 파일 형식
          </Typography>
          <List>
            <ListItem>
              <ListItemIcon>
                <InsertDriveFile color="primary" />
              </ListItemIcon>
              <ListItemText
                primary="CSV (Comma-Separated Values)"
                secondary="UTF-8, CP949 인코딩 지원"
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <InsertDriveFile color="primary" />
              </ListItemIcon>
              <ListItemText
                primary="Excel"
                secondary=".xls, .xlsx 형식 지원"
              />
            </ListItem>
          </List>
        </Paper>
      </DashboardLayout>
    );
  } catch (error) {
    console.error('FileUpload rendering error:', error);
    content = (
      <div className="file-upload-error">
        파일 업로드 컴포넌트 로드 중 오류가 발생했습니다.
      </div>
    );
  }
  return content;
};

export default FileUpload;