import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Button, 
  Typography, 
  Paper, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow,
  IconButton,
  Tooltip
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import Layout from '@/components/layout/Layout';
import { useRouter } from 'next/router';
import axios from 'axios';
import { useAuth } from '@/contexts/AuthContext';

interface Field {
  id: number;
  name: string;
  area: number;
  soil_type: string | null;
  crop_type: string | null;
  coordinates: Array<{lat: number, lng: number}>;
  created_at: string;
  updated_at: string;
}

const FieldsPage = () => {
  const [fields, setFields] = useState<Field[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    // 認証されていない場合はログインページにリダイレクト
    if (!isAuthenticated && !loading) {
      router.push('/login');
      return;
    }

    const fetchFields = async () => {
      try {
        const response = await axios.get(`http://localhost:8080/api/v1/fields/`);
        setFields(response.data);
      } catch (err: any) {
        setError(err.response?.data?.detail || '圃場データの取得に失敗しました');
      } finally {
        setLoading(false);
      }
    };

    if (isAuthenticated) {
      fetchFields();
    }
  }, [isAuthenticated, router, loading]);

  const handleDelete = async (id: number) => {
    if (window.confirm('この圃場を削除してもよろしいですか？')) {
      try {
        await axios.delete(`http://localhost:8080/api/v1/fields/${id}`);
        // 削除後にリストを更新
        setFields(fields.filter(field => field.id !== id));
      } catch (err: any) {
        setError(err.response?.data?.detail || '圃場の削除に失敗しました');
      }
    }
  };

  return (
    <Layout title="圃場管理">
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          圃場一覧
        </Typography>
        <Button 
          variant="contained" 
          startIcon={<AddIcon />}
          onClick={() => router.push('/fields/new')}
        >
          新規圃場登録
        </Button>
      </Box>

      {error && (
        <Typography color="error" sx={{ mb: 2 }}>
          {error}
        </Typography>
      )}

      <TableContainer component={Paper}>
        <Table sx={{ minWidth: 650 }} aria-label="圃場一覧">
          <TableHead>
            <TableRow>
              <TableCell>圃場名</TableCell>
              <TableCell align="right">面積 (ha)</TableCell>
              <TableCell>土壌タイプ</TableCell>
              <TableCell>作付作物</TableCell>
              <TableCell>最終更新日</TableCell>
              <TableCell align="center">操作</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={6} align="center">読み込み中...</TableCell>
              </TableRow>
            ) : fields.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center">登録されている圃場がありません</TableCell>
              </TableRow>
            ) : (
              fields.map((field) => (
                <TableRow
                  key={field.id}
                  sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                >
                  <TableCell component="th" scope="row">
                    {field.name}
                  </TableCell>
                  <TableCell align="right">{field.area.toFixed(2)}</TableCell>
                  <TableCell>{field.soil_type || '-'}</TableCell>
                  <TableCell>{field.crop_type || '-'}</TableCell>
                  <TableCell>{new Date(field.updated_at).toLocaleDateString()}</TableCell>
                  <TableCell align="center">
                    <Tooltip title="詳細表示">
                      <IconButton 
                        color="primary"
                        onClick={() => router.push(`/fields/${field.id}`)}
                      >
                        <EditIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="削除">
                      <IconButton 
                        color="error"
                        onClick={() => handleDelete(field.id)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Layout>
  );
};

export default FieldsPage;
