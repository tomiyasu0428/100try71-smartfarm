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
  CircularProgress,
  FormControl,
  InputLabel,
  Select
} from '@mui/material';
import { useRouter } from 'next/router';
import axios from 'axios';

// 資材・農機タイプの選択肢
const RESOURCE_TYPES = [
  { value: 'material', label: '資材' },
  { value: 'equipment', label: '農機' }
];

// カテゴリの選択肢
const RESOURCE_CATEGORIES = {
  material: [
    '肥料',
    '農薬',
    '種子',
    '苗',
    '土壌改良材',
    'マルチ資材',
    'その他資材'
  ],
  equipment: [
    'トラクター',
    '耕運機',
    '播種機',
    '防除機',
    '収穫機',
    '運搬車',
    'その他機械'
  ]
};

// 単位の選択肢
const UNITS = [
  'kg',
  'g',
  'L',
  'mL',
  '袋',
  '箱',
  '個',
  '台',
  '本',
  'セット'
];

export default function NewResourcePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  
  // フォームの状態
  const [formData, setFormData] = useState({
    name: '',
    type: 'material',
    category: '',
    quantity: '0',
    unit: '',
    purchase_date: '',
    purchase_price: '',
    supplier: '',
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

  // セレクトフィールドの変更ハンドラ
  const handleSelectChange = (e: any) => {
    const { name, value } = e.target;
    
    // タイプが変更された場合、カテゴリをリセット
    if (name === 'type') {
      setFormData({
        ...formData,
        [name]: value,
        category: ''
      });
    } else {
      setFormData({
        ...formData,
        [name]: value
      });
    }
  };

  // フォーム送信ハンドラ
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // 数値フィールドの変換
    const resourceData = {
      ...formData,
      quantity: parseFloat(formData.quantity) || 0,
      purchase_price: formData.purchase_price ? parseFloat(formData.purchase_price) : null,
      organization_id: 1 // 仮の組織ID（実際の認証システムから取得するべき）
    };
    
    try {
      setLoading(true);
      setError('');
      
      // APIリクエスト
      await axios.post('http://localhost:8080/api/v1/resources', resourceData);
      
      setSuccess(true);
      
      // 成功したら3秒後に一覧ページへリダイレクト
      setTimeout(() => {
        router.push('/resources');
      }, 3000);
      
    } catch (err) {
      console.error('資材・農機の登録に失敗しました', err);
      setError('資材・農機の登録に失敗しました。入力内容を確認してください。');
      setSuccess(false);
    } finally {
      setLoading(false);
    }
  };

  // キャンセルボタンのハンドラ
  const handleCancel = () => {
    router.push('/resources');
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          新規資材・農機登録
        </Typography>
        
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mb: 2 }}>資材・農機が正常に登録されました。一覧ページに戻ります...</Alert>}
        
        <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 3 }}>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6}>
              <TextField
                required
                fullWidth
                id="name"
                label="名称"
                name="name"
                value={formData.name}
                onChange={handleChange}
                disabled={loading}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth required disabled={loading}>
                <InputLabel id="type-label">種類</InputLabel>
                <Select
                  labelId="type-label"
                  id="type"
                  name="type"
                  value={formData.type}
                  onChange={handleSelectChange}
                  label="種類"
                >
                  {RESOURCE_TYPES.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth required disabled={loading}>
                <InputLabel id="category-label">カテゴリ</InputLabel>
                <Select
                  labelId="category-label"
                  id="category"
                  name="category"
                  value={formData.category}
                  onChange={handleSelectChange}
                  label="カテゴリ"
                >
                  {RESOURCE_CATEGORIES[formData.type as keyof typeof RESOURCE_CATEGORIES].map((category) => (
                    <MenuItem key={category} value={category}>
                      {category}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={3}>
              <TextField
                required
                fullWidth
                id="quantity"
                label="数量"
                name="quantity"
                type="number"
                value={formData.quantity}
                onChange={handleChange}
                disabled={loading}
                inputProps={{ min: 0, step: 0.01 }}
              />
            </Grid>
            <Grid item xs={12} sm={3}>
              <FormControl fullWidth required disabled={loading}>
                <InputLabel id="unit-label">単位</InputLabel>
                <Select
                  labelId="unit-label"
                  id="unit"
                  name="unit"
                  value={formData.unit}
                  onChange={handleSelectChange}
                  label="単位"
                >
                  {UNITS.map((unit) => (
                    <MenuItem key={unit} value={unit}>
                      {unit}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                id="purchase_date"
                label="購入日"
                name="purchase_date"
                type="date"
                value={formData.purchase_date}
                onChange={handleChange}
                disabled={loading}
                InputLabelProps={{
                  shrink: true,
                }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                id="purchase_price"
                label="購入価格"
                name="purchase_price"
                type="number"
                value={formData.purchase_price}
                onChange={handleChange}
                disabled={loading}
                inputProps={{ min: 0 }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                id="supplier"
                label="仕入先"
                name="supplier"
                value={formData.supplier}
                onChange={handleChange}
                disabled={loading}
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
              disabled={loading || !formData.name || !formData.category || !formData.unit}
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
