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
  Alert
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import { useRouter } from 'next/router';
import axios from 'axios';

// 作物データの型定義
interface Crop {
  id: number;
  name: string;
  category: string;
  growing_period: number;
  planting_season: string;
  harvesting_season: string;
}

export default function CropsPage() {
  const [crops, setCrops] = useState<Crop[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const router = useRouter();

  useEffect(() => {
    // 作物データの取得
    const fetchCrops = async () => {
      try {
        setLoading(true);
        const response = await axios.get('http://localhost:8080/api/v1/crops');
        setCrops(response.data);
        setError('');
      } catch (err) {
        console.error('作物データの取得に失敗しました', err);
        setError('作物データの取得に失敗しました。バックエンドサーバーが起動しているか確認してください。');
        setCrops([]);
      } finally {
        setLoading(false);
      }
    };

    fetchCrops();
  }, []);

  // 新規作物登録ページへ遷移
  const handleAddCrop = () => {
    router.push('/crops/new');
  };

  // 作物詳細ページへ遷移
  const handleRowClick = (id: number) => {
    router.push(`/crops/${id}`);
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" gutterBottom>
          作物管理
        </Typography>
        <Button 
          variant="contained" 
          color="primary" 
          startIcon={<AddIcon />}
          onClick={handleAddCrop}
        >
          新規作物登録
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
                <TableCell>カテゴリ</TableCell>
                <TableCell>生育期間（日）</TableCell>
                <TableCell>植付時期</TableCell>
                <TableCell>収穫時期</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {crops.length > 0 ? (
                crops.map((crop) => (
                  <TableRow 
                    key={crop.id}
                    hover
                    onClick={() => handleRowClick(crop.id)}
                    sx={{ cursor: 'pointer' }}
                  >
                    <TableCell>{crop.id}</TableCell>
                    <TableCell>{crop.name}</TableCell>
                    <TableCell>{crop.category}</TableCell>
                    <TableCell>{crop.growing_period}</TableCell>
                    <TableCell>{crop.planting_season}</TableCell>
                    <TableCell>{crop.harvesting_season}</TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    登録されている作物がありません
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
