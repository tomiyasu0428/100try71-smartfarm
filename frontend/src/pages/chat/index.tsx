import { useState, useEffect, useRef } from 'react';
import { 
  Box, 
  Typography, 
  Container, 
  Paper, 
  TextField,
  Button,
  List,
  ListItem,
  ListItemText,
  Divider,
  CircularProgress,
  Alert,
  Grid,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  InputAdornment
} from '@mui/material';
import { Send as SendIcon, Add as AddIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { useRouter } from 'next/router';
import axios from 'axios';

interface ChatSession {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
  messages: ChatMessage[];
}

interface ChatMessage {
  id: number;
  content: string;
  is_from_ai: boolean;
  created_at: string;
}

export default function ChatPage() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [newSessionDialogOpen, setNewSessionDialogOpen] = useState(false);
  const [newSessionTitle, setNewSessionTitle] = useState('');
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [sessionToDelete, setSessionToDelete] = useState<number | null>(null);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  useEffect(() => {
    fetchSessions();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [currentSession?.messages]);

  const fetchSessions = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:8080/api/v1/chat/sessions');
      setSessions(response.data);
      
      if (response.data.length > 0 && !currentSession) {
        fetchSession(response.data[0].id);
      }
      
      setError('');
    } catch (err) {
      console.error('チャットセッションの取得に失敗しました', err);
      setError('チャットセッションの取得に失敗しました。バックエンドサーバーが起動しているか確認してください。');
    } finally {
      setLoading(false);
    }
  };

  const fetchSession = async (sessionId: number) => {
    try {
      setLoading(true);
      const response = await axios.get(`http://localhost:8080/api/v1/chat/sessions/${sessionId}`);
      setCurrentSession(response.data);
      setError('');
    } catch (err) {
      console.error('チャットセッションの取得に失敗しました', err);
      setError('チャットセッションの取得に失敗しました。');
    } finally {
      setLoading(false);
    }
  };

  const createSession = async () => {
    if (!newSessionTitle.trim()) {
      return;
    }
    
    try {
      setLoading(true);
      const response = await axios.post('http://localhost:8080/api/v1/chat/sessions', {
        title: newSessionTitle
      });
      
      setSessions([response.data, ...sessions]);
      setCurrentSession(response.data);
      setNewSessionTitle('');
      setNewSessionDialogOpen(false);
      setError('');
    } catch (err) {
      console.error('チャットセッションの作成に失敗しました', err);
      setError('チャットセッションの作成に失敗しました。');
    } finally {
      setLoading(false);
    }
  };

  const deleteSession = async () => {
    if (sessionToDelete === null) {
      return;
    }
    
    try {
      setLoading(true);
      await axios.delete(`http://localhost:8080/api/v1/chat/sessions/${sessionToDelete}`);
      
      const updatedSessions = sessions.filter(session => session.id !== sessionToDelete);
      setSessions(updatedSessions);
      
      if (currentSession && currentSession.id === sessionToDelete) {
        setCurrentSession(updatedSessions.length > 0 ? updatedSessions[0] : null);
        if (updatedSessions.length > 0) {
          fetchSession(updatedSessions[0].id);
        }
      }
      
      setSessionToDelete(null);
      setDeleteDialogOpen(false);
      setError('');
    } catch (err) {
      console.error('チャットセッションの削除に失敗しました', err);
      setError('チャットセッションの削除に失敗しました。');
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!message.trim() || !currentSession) {
      return;
    }
    
    try {
      setLoading(true);
      await axios.post(`http://localhost:8080/api/v1/chat/sessions/${currentSession.id}/messages`, {
        content: message,
        is_from_ai: false
      });
      
      fetchSession(currentSession.id);
      setMessage('');
    } catch (err) {
      console.error('メッセージの送信に失敗しました', err);
      setError('メッセージの送信に失敗しました。');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('ja-JP');
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        AIチャットアシスタント
      </Typography>
      
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      
      <Grid container spacing={2} sx={{ height: 'calc(100vh - 200px)' }}>
        {/* セッション一覧 */}
        <Grid item xs={12} md={3}>
          <Paper sx={{ height: '100%', overflow: 'auto', p: 2 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">チャット履歴</Typography>
              <Button 
                variant="contained" 
                size="small"
                startIcon={<AddIcon />}
                onClick={() => setNewSessionDialogOpen(true)}
              >
                新規
              </Button>
            </Box>
            
            <List>
              {sessions.length > 0 ? (
                sessions.map((session) => (
                  <Box key={session.id}>
                    <ListItem 
                      button 
                      selected={currentSession?.id === session.id}
                      onClick={() => fetchSession(session.id)}
                      secondaryAction={
                        <IconButton 
                          edge="end" 
                          aria-label="delete"
                          onClick={(e) => {
                            e.stopPropagation();
                            setSessionToDelete(session.id);
                            setDeleteDialogOpen(true);
                          }}
                        >
                          <DeleteIcon />
                        </IconButton>
                      }
                    >
                      <ListItemText 
                        primary={session.title} 
                        secondary={formatDate(session.updated_at)}
                        primaryTypographyProps={{
                          noWrap: true,
                          style: { maxWidth: '150px' }
                        }}
                      />
                    </ListItem>
                    <Divider />
                  </Box>
                ))
              ) : (
                <Typography variant="body2" color="text.secondary" align="center">
                  チャット履歴がありません
                </Typography>
              )}
            </List>
          </Paper>
        </Grid>
        
        {/* チャット画面 */}
        <Grid item xs={12} md={9}>
          <Paper sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            {/* メッセージ表示エリア */}
            <Box sx={{ 
              flexGrow: 1, 
              p: 2, 
              overflow: 'auto',
              display: 'flex',
              flexDirection: 'column'
            }}>
              {currentSession ? (
                currentSession.messages.length > 0 ? (
                  currentSession.messages.map((msg) => (
                    <Box 
                      key={msg.id}
                      sx={{ 
                        alignSelf: msg.is_from_ai ? 'flex-start' : 'flex-end',
                        maxWidth: '70%',
                        mb: 2
                      }}
                    >
                      <Paper 
                        elevation={1}
                        sx={{ 
                          p: 2,
                          bgcolor: msg.is_from_ai ? 'grey.100' : 'primary.light',
                          color: msg.is_from_ai ? 'text.primary' : 'white'
                        }}
                      >
                        <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                          {msg.content}
                        </Typography>
                        <Typography variant="caption" color={msg.is_from_ai ? 'text.secondary' : 'rgba(255,255,255,0.7)'} sx={{ display: 'block', mt: 1, textAlign: 'right' }}>
                          {formatDate(msg.created_at)}
                        </Typography>
                      </Paper>
                    </Box>
                  ))
                ) : (
                  <Box sx={{ 
                    display: 'flex', 
                    flexDirection: 'column', 
                    justifyContent: 'center', 
                    alignItems: 'center',
                    height: '100%'
                  }}>
                    <Typography variant="body1" color="text.secondary">
                      AIアシスタントに農業に関する質問をしてみましょう
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      例: 「トマトの栽培方法について教えて」「病害虫対策のアドバイスが欲しい」
                    </Typography>
                  </Box>
                )
              ) : (
                <Box sx={{ 
                  display: 'flex', 
                  justifyContent: 'center', 
                  alignItems: 'center',
                  height: '100%'
                }}>
                  <Typography variant="body1" color="text.secondary">
                    チャットセッションを選択するか、新規作成してください
                  </Typography>
                </Box>
              )}
              <div ref={messagesEndRef} />
            </Box>
            
            {/* メッセージ入力エリア */}
            <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
              <TextField
                fullWidth
                multiline
                maxRows={4}
                placeholder="メッセージを入力..."
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                disabled={!currentSession || loading}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton 
                        color="primary" 
                        onClick={sendMessage}
                        disabled={!message.trim() || !currentSession || loading}
                      >
                        {loading ? <CircularProgress size={24} /> : <SendIcon />}
                      </IconButton>
                    </InputAdornment>
                  )
                }}
              />
            </Box>
          </Paper>
        </Grid>
      </Grid>
      
      {/* 新規セッション作成ダイアログ */}
      <Dialog open={newSessionDialogOpen} onClose={() => setNewSessionDialogOpen(false)}>
        <DialogTitle>新規チャットセッション</DialogTitle>
        <DialogContent>
          <DialogContentText>
            新しいチャットセッションのタイトルを入力してください。
          </DialogContentText>
          <TextField
            autoFocus
            margin="dense"
            label="タイトル"
            fullWidth
            value={newSessionTitle}
            onChange={(e) => setNewSessionTitle(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                createSession();
              }
            }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setNewSessionDialogOpen(false)}>キャンセル</Button>
          <Button 
            onClick={createSession} 
            disabled={!newSessionTitle.trim() || loading}
            variant="contained"
          >
            作成
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* セッション削除確認ダイアログ */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>チャットセッションの削除</DialogTitle>
        <DialogContent>
          <DialogContentText>
            このチャットセッションを削除してもよろしいですか？この操作は元に戻せません。
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>キャンセル</Button>
          <Button 
            onClick={deleteSession} 
            color="error"
            variant="contained"
          >
            削除
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}
