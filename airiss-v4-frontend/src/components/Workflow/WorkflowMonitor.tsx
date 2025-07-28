import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  LinearProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Button,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import api from '../../services/api';

interface WorkflowJob {
  job_id: string;
  status: string;
  created_at: string;
  completed_at?: string;
  download_url?: string;
  task_summary: {
    total: number;
    by_status: Record<string, number>;
  };
  error?: string;
}

interface WorkflowTask {
  id: string;
  job_id: string;
  task_type: string;
  status: string;
  priority: string;
  retry_count: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
}

interface WorkflowMetrics {
  total_jobs: number;
  active_jobs: number;
  completed_jobs: number;
  failed_jobs: number;
  task_metrics: {
    total_tasks: number;
    running_tasks: number;
    status_counts: Record<string, number>;
    by_type: Record<string, { count: number; avg_retries: number }>;
    queue_sizes: Record<string, number>;
  };
  worker_status: {
    active_workers: number;
    is_running: boolean;
  };
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const WorkflowMonitor: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [jobs, setJobs] = useState<WorkflowJob[]>([]);
  const [selectedJob, setSelectedJob] = useState<WorkflowJob | null>(null);
  const [tasks, setTasks] = useState<WorkflowTask[]>([]);
  const [metrics, setMetrics] = useState<WorkflowMetrics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadJobs();
    loadMetrics();
    const interval = setInterval(() => {
      loadJobs();
      loadMetrics();
    }, 5000); // 5초마다 갱신

    return () => clearInterval(interval);
  }, []);

  const loadJobs = async () => {
    try {
      const response = await api.get('/api/v1/workflow/jobs');
      setJobs(response.data);
    } catch (err: any) {
      console.error('Failed to load jobs:', err);
    }
  };

  const loadMetrics = async () => {
    try {
      const response = await api.get('/api/v1/workflow/metrics');
      setMetrics(response.data);
    } catch (err: any) {
      console.error('Failed to load metrics:', err);
    }
  };

  const loadJobTasks = async (jobId: string) => {
    setLoading(true);
    try {
      const response = await api.get(`/api/v1/workflow/jobs/${jobId}/tasks`);
      setTasks(response.data);
    } catch (err: any) {
      setError('Failed to load tasks');
    } finally {
      setLoading(false);
    }
  };

  const retryJob = async (jobId: string) => {
    try {
      await api.post(`/api/v1/workflow/jobs/${jobId}/retry`);
      loadJobs();
      if (selectedJob?.job_id === jobId) {
        loadJobTasks(jobId);
      }
    } catch (err: any) {
      setError('Failed to retry job');
    }
  };

  const cancelJob = async (jobId: string) => {
    try {
      await api.delete(`/api/v1/workflow/jobs/${jobId}`);
      loadJobs();
      setSelectedJob(null);
      setTasks([]);
    } catch (err: any) {
      setError('Failed to cancel job');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'running':
        return 'primary';
      case 'failed':
        return 'error';
      case 'pending':
        return 'default';
      case 'retrying':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getProgressValue = (job: WorkflowJob) => {
    if (!job.task_summary?.total) return 0;
    const completed = job.task_summary.by_status?.completed || 0;
    return (completed / job.task_summary.total) * 100;
  };

  return (
    <Box sx={{ width: '100%' }}>
      <Typography variant="h4" gutterBottom>
        Workflow Monitor
      </Typography>

      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Tabs value={tabValue} onChange={(_, v) => setTabValue(v)}>
        <Tab label="Jobs" />
        <Tab label="System Metrics" />
      </Tabs>

      <TabPanel value={tabValue} index={0}>
        {/* Jobs List */}
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                  <Typography variant="h6">Active Jobs</Typography>
                  <IconButton onClick={loadJobs}>
                    <RefreshIcon />
                  </IconButton>
                </Box>

                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Job ID</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Progress</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {jobs.map((job) => (
                        <TableRow
                          key={job.job_id}
                          hover
                          selected={selectedJob?.job_id === job.job_id}
                          onClick={() => {
                            setSelectedJob(job);
                            loadJobTasks(job.job_id);
                          }}
                          sx={{ cursor: 'pointer' }}
                        >
                          <TableCell>{job.job_id.slice(0, 8)}...</TableCell>
                          <TableCell>
                            <Chip
                              label={job.status}
                              color={getStatusColor(job.status) as any}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <LinearProgress
                              variant="determinate"
                              value={getProgressValue(job)}
                              sx={{ minWidth: 100 }}
                            />
                          </TableCell>
                          <TableCell>
                            {job.status === 'failed' && (
                              <IconButton
                                size="small"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  retryJob(job.job_id);
                                }}
                              >
                                <PlayIcon />
                              </IconButton>
                            )}
                            {job.status === 'running' && (
                              <IconButton
                                size="small"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  cancelJob(job.job_id);
                                }}
                              >
                                <StopIcon />
                              </IconButton>
                            )}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            {selectedJob && (
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Job Details
                  </Typography>

                  <Box mb={2}>
                    <Typography variant="body2" color="textSecondary">
                      Job ID: {selectedJob.job_id}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Created: {format(new Date(selectedJob.created_at), 'PPpp')}
                    </Typography>
                    {selectedJob.completed_at && (
                      <Typography variant="body2" color="textSecondary">
                        Completed: {format(new Date(selectedJob.completed_at), 'PPpp')}
                      </Typography>
                    )}
                    {selectedJob.error && (
                      <Alert severity="error" sx={{ mt: 1 }}>
                        {selectedJob.error}
                      </Alert>
                    )}
                    {selectedJob.download_url && (
                      <Button
                        variant="contained"
                        color="primary"
                        href={selectedJob.download_url}
                        target="_blank"
                        sx={{ mt: 1 }}
                      >
                        Download Result
                      </Button>
                    )}
                  </Box>

                  <Typography variant="subtitle1" gutterBottom>
                    Tasks
                  </Typography>

                  {loading ? (
                    <CircularProgress />
                  ) : (
                    <TableContainer component={Paper} variant="outlined">
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            <TableCell>Type</TableCell>
                            <TableCell>Status</TableCell>
                            <TableCell>Retries</TableCell>
                            <TableCell>Duration</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {tasks.map((task) => (
                            <TableRow key={task.id}>
                              <TableCell>{task.task_type}</TableCell>
                              <TableCell>
                                <Chip
                                  label={task.status}
                                  color={getStatusColor(task.status) as any}
                                  size="small"
                                />
                              </TableCell>
                              <TableCell>{task.retry_count}</TableCell>
                              <TableCell>
                                {task.started_at && task.completed_at
                                  ? `${Math.round(
                                      (new Date(task.completed_at).getTime() -
                                        new Date(task.started_at).getTime()) /
                                        1000
                                    )}s`
                                  : '-'}
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  )}
                </CardContent>
              </Card>
            )}
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        {/* System Metrics */}
        {metrics && (
          <Grid container spacing={3}>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Total Jobs
                  </Typography>
                  <Typography variant="h4">{metrics.total_jobs}</Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Active Jobs
                  </Typography>
                  <Typography variant="h4">{metrics.active_jobs}</Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Completed Jobs
                  </Typography>
                  <Typography variant="h4">{metrics.completed_jobs}</Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Failed Jobs
                  </Typography>
                  <Typography variant="h4" color="error">
                    {metrics.failed_jobs}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Task Status Distribution
                  </Typography>
                  <TableContainer>
                    <Table size="small">
                      <TableBody>
                        {Object.entries(metrics.task_metrics.status_counts || {}).map(
                          ([status, count]) => (
                            <TableRow key={status}>
                              <TableCell>{status}</TableCell>
                              <TableCell align="right">{count}</TableCell>
                            </TableRow>
                          )
                        )}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Worker Status
                  </Typography>
                  <Box>
                    <Typography variant="body2">
                      Active Workers: {metrics.worker_status.active_workers}
                    </Typography>
                    <Typography variant="body2">
                      System Status:{' '}
                      <Chip
                        label={metrics.worker_status.is_running ? 'Running' : 'Stopped'}
                        color={metrics.worker_status.is_running ? 'success' : 'error'}
                        size="small"
                      />
                    </Typography>
                  </Box>

                  <Typography variant="subtitle1" sx={{ mt: 2 }}>
                    Queue Sizes
                  </Typography>
                  <TableContainer>
                    <Table size="small">
                      <TableBody>
                        {Object.entries(metrics.task_metrics.queue_sizes || {}).map(
                          ([priority, size]) => (
                            <TableRow key={priority}>
                              <TableCell>{priority}</TableCell>
                              <TableCell align="right">{size}</TableCell>
                            </TableRow>
                          )
                        )}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}
      </TabPanel>
    </Box>
  );
};

export default WorkflowMonitor;