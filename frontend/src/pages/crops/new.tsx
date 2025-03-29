import { useState } from 'react';
import { 
  Box, 
  Typography, 
  Container, 
  Paper, 
  TextField,
  Button,
  Grid,
  MenuItem,
  Alert,
  CircularProgress
} from '@mui/material';
import { useRouter } from 'next/router';
import axios from 'axios';

// 作物カテゴリの選択肢
const CROP_CATEGORIES = [
  '穀物',
  '野菜',
  '果物',
  '豆類',
  'その他'
];

export default function NewCropPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  
  // フォームの状態
  const [formData, setFormData] = useState({
    name: '',
    category: '',
    growing_period: '',
    planting_season: '',
    harvesting_season: '',
    notes: ''
  });

  // 入力フィールドの変更ハンドラ
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  // フォーム送信ハンドラ
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // 数値フィールドの変換
    const cropData = {
      ...formData,
      growing_period: parseInt(formData.growing_period) || 0,
      organization_id: 1 // 仮の組織ID（実際の認証システムから取得するべき）
    };
    
    try {
      setLoading(true);
      setError('');
      
      // APIリクエスト
      await axios.post('http://localhost:8080/api/v1/crops', cropData);
      
      setSuccess(true);
      
      // 成功したら3秒後に一覧ページへリダイレクト
      setTimeout(() => {
        router.push('/crops');
      }, 3000);
      
    } catch (err) {
      console.error('作物の登録に失敗しました', err);
      setError('作物の登録に失敗しました。入力内容を確認してください。');
      setSuccess(false);
    } finally {
      setLoading(false);
    }
  };

  // キャンセルボタンのハンドラ
  const handleCancel = () => {
    router.push('/crops');
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          新規作物登録
        </Typography>
        
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mb: 2 }}>作物が正常に登録されました。一覧ページに戻ります...</Alert>}
        
        <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 3 }}>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6}>
              <TextField
                required
                fullWidth
                id="name"
                label="作物名"
                name="name"
                value={formData.name}
                onChange={handleChange}
                disabled={loading}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                required
                fullWidth
                select
                id="category"
                label="カテゴリ"
                name="category"
                value={formData.category}
                onChange={handleChange}
                disabled={loading}
              >
                {CROP_CATEGORIES.map((option) => (
                  <MenuItem key={option} value={option}>
                    {option}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                required
                fullWidth
                id="growing_period"
                label="生育期間（日）"
                name="growing_period"
                type="number"
                value={formData.growing_period}
                onChange={handleChange}
                disabled={loading}
                inputProps={{ min: 0 }}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                required
                fullWidth
                id="planting_season"
                label="植付時期"
                name="planting_season"
                value={formData.planting_season}
                onChange={handleChange}
                disabled={loading}
                placeholder="例: 4月-5月"
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                required
                fullWidth
                id="harvesting_season"
                label="収穫時期"
                name="harvesting_season"
                value={formData.harvesting_season}
                onChange={handleChange}
                disabled={loading}
                placeholder="例: 9月-10月"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                id="notes"
                label="備考"
                name="notes"
                multiline
                rows={4}
                value={formData.notes}
                onChange={handleChange}
                disabled={loading}
              />
            </Grid>
          </Grid>
          
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 3, gap: 2 }}>
            <Button
              variant="outlined"
              onClick={handleCancel}
              disabled={loading}
            >
              キャンセル
            </Button>
            <Button
              type="submit"
              variant="contained"
              disabled={loading || !formData.name || !formData.category}
              startIcon={loading ? <CircularProgress size={20} /> : null}
            >
              {loading ? '登録中...' : '登録'}
            </Button>
          </Box>
        </Box>
      </Paper>
    </Container>
  );
}
