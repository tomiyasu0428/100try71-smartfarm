import { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Container, 
  Paper, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow,
  Button,
  CircularProgress,
  Alert,
  Chip
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import { useRouter } from 'next/router';
import axios from 'axios';

// 資材・農機データの型定義
interface Resource {
  id: number;
  name: string;
  type: string;
  category: string;
  quantity: number;
  unit: string;
  notes: string;
}

// タイプに応じた色を返す関数
const getTypeColor = (type: string) => {
  switch (type) {
    case 'material':
      return 'primary';
    case 'equipment':
      return 'secondary';
    default:
      return 'default';
  }
};

// タイプの日本語表示
const getTypeLabel = (type: string) => {
  switch (type) {
    case 'material':
      return '資材';
    case 'equipment':
      return '農機';
    default:
      return type;
  }
};

export default function ResourcesPage() {
  const [resources, setResources] = useState<Resource[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const router = useRouter();

  useEffect(() => {
    // 資材・農機データの取得
    const fetchResources = async () => {
      try {
        setLoading(true);
        const response = await axios.get('http://localhost:8080/api/v1/resources');
        setResources(response.data);
        setError('');
      } catch (err) {
        console.error('資材・農機データの取得に失敗しました', err);
        setError('資材・農機データの取得に失敗しました。バックエンドサーバーが起動しているか確認してください。');
        setResources([]);
      } finally {
        setLoading(false);
      }
    };

    fetchResources();
  }, []);

  // 新規資材・農機登録ページへ遷移
  const handleAddResource = () => {
    router.push('/resources/new');
  };

  // 資材・農機詳細ページへ遷移
  const handleRowClick = (id: number) => {
    router.push(`/resources/${id}`);
  };

  // 数量と単位の表示
  const formatQuantity = (quantity: number, unit: string) => {
    return `${quantity} ${unit}`;
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" gutterBottom>
          資材・農機管理
        </Typography>
        <Button 
          variant="contained" 
          color="primary" 
          startIcon={<AddIcon />}
          onClick={handleAddResource}
        >
          新規登録
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {loading ? (
        <Box display="flex" justifyContent="center" my={4}>
          <CircularProgress />
        </Box>
      ) : (
        <TableContainer component={Paper}>
          <Table sx={{ minWidth: 650 }}>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>名称</TableCell>
                <TableCell>種類</TableCell>
                <TableCell>カテゴリ</TableCell>
                <TableCell>数量</TableCell>
                <TableCell>備考</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {resources.length > 0 ? (
                resources.map((resource) => (
                  <TableRow 
                    key={resource.id}
                    hover
                    onClick={() => handleRowClick(resource.id)}
                    sx={{ cursor: 'pointer' }}
                  >
                    <TableCell>{resource.id}</TableCell>
                    <TableCell>{resource.name}</TableCell>
                    <TableCell>
                      <Chip 
                        label={getTypeLabel(resource.type)} 
                        color={getTypeColor(resource.type) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{resource.category}</TableCell>
                    <TableCell>{formatQuantity(resource.quantity, resource.unit)}</TableCell>
                    <TableCell>{resource.notes}</TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    登録されている資材・農機がありません
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Container>
  );
}
