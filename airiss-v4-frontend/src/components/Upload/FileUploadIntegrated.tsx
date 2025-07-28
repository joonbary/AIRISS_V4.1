import React, { useState, useCallback, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Paper,
  Typography,
  Button,
  LinearProgress,
  Alert,
  Grid,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Tooltip,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  CloudUpload,
  InsertDriveFile,
  CheckCircle,
  Error as ErrorIcon,
  Visibility,
  Delete,
  Analytics,
  FilePresent,
  TableChart,
  ExpandMore,
  Info
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import { authAPI, analysisAPI, handleAPIError } from '../../services/api_v4';
import DashboardLayout from '../Layout/DashboardLayout';

interface FileUploadResponse {
  job_id: string;
  status: string;
  filename: string;
  message?: string;
}

interface FileInfo {
  id: string;
  filename: string;
  upload_time: string;
  total_records: number;
  size: number;
  status?: string;
}

interface FileUploadIntegratedProps {
  onUploadSuccess?: (data: {
    fileId: string;
    fileName: string;
    totalRecords: number;
    columns: string[];
  }) => void;
}

const FileUploadIntegrated: React.FC<FileUploadIntegratedProps> = ({ onUploadSuccess }) => {
  const navigate = useNavigate();
  
  // Upload state
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [fileInfo, setFileInfo] = useState<FileUploadResponse | null>(null);
  
  // File list state
  const [existingFiles, setExistingFiles] = useState<FileInfo[]>([]);
  const [isLoadingFiles, setIsLoadingFiles] = useState(true);
  const [selectedFileForPreview, setSelectedFileForPreview] = useState<FileInfo | null>(null);
  const [previewDialogOpen, setPreviewDialogOpen] = useState(false);

  // Load existing files
  useEffect(() => {
    loadExistingFiles();
  }, []);

  const loadExistingFiles = async () => {
    try {
      setIsLoadingFiles(true);
      // Note: We'll need to implement getFiles endpoint in the backend
      // For now, we'll use an empty array
      setExistingFiles([]);
    } catch (error) {
      console.error('Failed to load existing files:', error);
    } finally {
      setIsLoadingFiles(false);
    }
  };

  // File drop handler
  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles?.length === 0) return;

    const file = acceptedFiles[0];
    
    // File size validation (100MB)
    if (file.size > 100 * 1024 * 1024) {
      setError('파일 크기는 100MB를 초과할 수 없습니다.');
      return;
    }

    // File type validation
    const validTypes = [
      'text/csv',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ];
    
    if (!validTypes.includes(file.type) && !file.name.match(/\.(csv|xls|xlsx)$/)) {
      setError('CSV 또는 Excel 파일만 업로드 가능합니다.');
      return;
    }

    setError(null);
    setUploadStatus('uploading');
    setUploadProgress(0);

    // Progress simulation
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
      const response = await analysisAPI.uploadFile(file, (progress) => {
        setUploadProgress(Math.min(progress, 90));
      });
      console.log('📡 Upload Response:', response);
      
      setFileInfo(response);
      setUploadProgress(100);
      setUploadStatus('success');
      
      // Reload file list
      await loadExistingFiles();
      
      if (onUploadSuccess) {
        onUploadSuccess({
          fileId: response.job_id,
          fileName: response.filename,
          totalRecords: 0, // Will be available after analysis
          columns: []
        });
      }
    } catch (err: any) {
      console.error('Upload error:', err);
      setError(handleAPIError(err));
      setUploadStatus('error');
    } finally {
      clearInterval(progressInterval);
    }
  }, [onUploadSuccess]);

  // Dropzone configuration
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx']
    },
    multiple: false
  });

  // Handle file deletion
  const handleDeleteFile = async (fileId: string) => {
    try {
      // Note: We'll need to implement deleteFile endpoint in the backend
      console.log('Delete file:', fileId);
      await loadExistingFiles();
      
      // Clear current upload if it was deleted
      if (fileInfo?.job_id === fileId) {
        setFileInfo(null);
        setUploadStatus('idle');
      }
    } catch (error) {
      console.error('Failed to delete file:', error);
      setError('파일 삭제에 실패했습니다.');
    }
  };

  // Handle file preview
  const handlePreviewFile = (file: FileInfo) => {
    setSelectedFileForPreview(file);
    setPreviewDialogOpen(true);
  };

  // Utility functions
  const formatFileSize = (bytes?: number) => {
    if (!bytes || typeof bytes !== 'number') return '0 KB';
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)).toString());
    return Math.round((bytes / Math.pow(1024, i)) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDate = (date?: string) => {
    if (!date) return '-';
    try {
      return new Date(date).toLocaleString();
    } catch (error) {
      return '-';
    }
  };

  const getFileIcon = (filename: string) => {
    if (filename.toLowerCase().endsWith('.csv')) {
      return <TableChart color="success" />;
    }
    return <InsertDriveFile color="primary" />;
  };

  return (
    <DashboardLayout>
      <Box sx={{ maxWidth: 1200, mx: 'auto' }}>
        {/* Header */}
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
            <CloudUpload sx={{ mr: 2, color: 'primary.main' }} />
            파일 업로드
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Excel 또는 CSV 파일을 업로드하여 HR 분석을 시작하세요.
          </Typography>
        </Paper>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {/* Upload Area */}
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            새 파일 업로드
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
              transition: 'all 0.3s ease',
              '&:hover': {
                borderColor: 'primary.main',
                backgroundColor: 'action.hover'
              }
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

          {/* Upload Progress */}
          {uploadStatus === 'uploading' && (
            <Box sx={{ mb: 2 }}>
              <LinearProgress variant="determinate" value={uploadProgress} />
              <Typography variant="body2" sx={{ mt: 1 }}>
                업로드 중... {uploadProgress}%
              </Typography>
            </Box>
          )}

          {/* Upload Success */}
          {fileInfo && uploadStatus === 'success' && (
            <Alert severity="success" sx={{ mb: 2 }}>
              <Typography variant="h6" gutterBottom>
                파일 업로드 완료!
              </Typography>
              <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2">
                    <strong>파일명:</strong> {fileInfo.filename}
                  </Typography>
                  <Typography variant="body2">
                    <strong>작업 ID:</strong> {fileInfo.job_id}
                  </Typography>
                  <Typography variant="body2">
                    <strong>상태:</strong> {fileInfo.status}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    <Chip label="업로드 완료" size="small" color="success" />
                    <Chip label="분석 준비" size="small" color="primary" />
                  </Box>
                </Grid>
              </Grid>
              
              <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
                <Button
                  variant="contained"
                  startIcon={<Analytics />}
                  onClick={() => navigate(`/analysis?jobId=${fileInfo.job_id}`)}
                >
                  지금 분석하기
                </Button>
                <Button
                  variant="outlined"
                  onClick={() => {
                    setFileInfo(null);
                    setUploadStatus('idle');
                  }}
                >
                  다른 파일 업로드
                </Button>
              </Box>
            </Alert>
          )}

          {/* File Format Info */}
          <Accordion sx={{ mt: 2 }}>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Info sx={{ mr: 1, color: 'info.main' }} />
                <Typography variant="subtitle2">지원되는 파일 형식 및 요구사항</Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    파일 형식
                  </Typography>
                  <Box sx={{ pl: 2 }}>
                    <Typography variant="body2">• CSV (UTF-8, CP949 인코딩)</Typography>
                    <Typography variant="body2">• Excel (.xls, .xlsx)</Typography>
                    <Typography variant="body2">• 최대 파일 크기: 100MB</Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    필수 컬럼
                  </Typography>
                  <Box sx={{ pl: 2 }}>
                    <Typography variant="body2">• UID 컬럼 (직원 식별자)</Typography>
                    <Typography variant="body2">• 의견/평가 컬럼 (텍스트 데이터)</Typography>
                    <Typography variant="body2">• 점수/등급 컬럼 (선택사항)</Typography>
                  </Box>
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
        </Paper>

        {/* Existing Files */}
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            업로드된 파일 목록
          </Typography>
          
          {isLoadingFiles ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography>파일 목록을 불러오는 중...</Typography>
            </Box>
          ) : existingFiles.length === 0 ? (
            <Alert severity="info">
              업로드된 파일이 없습니다. 첫 번째 파일을 업로드해보세요!
            </Alert>
          ) : (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>파일명</TableCell>
                    <TableCell align="center">레코드 수</TableCell>
                    <TableCell align="center">파일 크기</TableCell>
                    <TableCell align="center">업로드 시간</TableCell>
                    <TableCell align="center">작업</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {existingFiles.map((file) => (
                    <TableRow key={file.id} hover>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          {getFileIcon(file.filename)}
                          <Typography sx={{ ml: 1 }}>{file.filename}</Typography>
                        </Box>
                      </TableCell>
                      <TableCell align="center">
                        {file.total_records.toLocaleString()}
                      </TableCell>
                      <TableCell align="center">
                        {formatFileSize(file.size)}
                      </TableCell>
                      <TableCell align="center">
                        {formatDate(file.upload_time)}
                      </TableCell>
                      <TableCell align="center">
                        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1 }}>
                          <Tooltip title="파일 정보 보기">
                            <IconButton
                              size="small"
                              onClick={() => handlePreviewFile(file)}
                            >
                              <Visibility />
                            </IconButton>
                          </Tooltip>
                          
                          <Tooltip title="분석하기">
                            <IconButton
                              size="small"
                              color="primary"
                              onClick={() => navigate(`/analysis?fileId=${file.id}`)}
                            >
                              <Analytics />
                            </IconButton>
                          </Tooltip>
                          
                          <Tooltip title="파일 삭제">
                            <IconButton
                              size="small"
                              color="error"
                              onClick={() => handleDeleteFile(file.id)}
                            >
                              <Delete />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </Paper>

        {/* File Preview Dialog */}
        <Dialog
          open={previewDialogOpen}
          onClose={() => setPreviewDialogOpen(false)}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <FilePresent sx={{ mr: 1 }} />
              파일 정보: {selectedFileForPreview?.filename}
            </Box>
          </DialogTitle>
          <DialogContent>
            {selectedFileForPreview && (
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle2" gutterBottom>
                        기본 정보
                      </Typography>
                      <Typography variant="body2">
                        <strong>파일명:</strong> {selectedFileForPreview.filename}
                      </Typography>
                      <Typography variant="body2">
                        <strong>레코드 수:</strong> {selectedFileForPreview.total_records.toLocaleString()}개
                      </Typography>
                      <Typography variant="body2">
                        <strong>파일 크기:</strong> {formatFileSize(selectedFileForPreview.size)}
                      </Typography>
                      <Typography variant="body2">
                        <strong>업로드 시간:</strong> {formatDate(selectedFileForPreview.upload_time)}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle2" gutterBottom>
                        분석 가능 여부
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <CheckCircle color="success" sx={{ mr: 1, fontSize: 16 }} />
                        <Typography variant="body2">분석 준비 완료</Typography>
                      </Box>
                      <Button
                        variant="contained"
                        size="small"
                        startIcon={<Analytics />}
                        onClick={() => {
                          setPreviewDialogOpen(false);
                          navigate(`/analysis?fileId=${selectedFileForPreview.id}`);
                        }}
                      >
                        분석 시작
                      </Button>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setPreviewDialogOpen(false)}>
              닫기
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </DashboardLayout>
  );
};

export default FileUploadIntegrated;