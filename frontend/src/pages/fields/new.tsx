import React, { useState, useCallback, useRef, useEffect } from 'react';
import { 
  Box, 
  Button, 
  TextField, 
  Typography, 
  Paper, 
  Grid,
  Alert,
  CircularProgress
} from '@mui/material';
import Layout from '@/components/layout/Layout';
import { useRouter } from 'next/router';
import axios from 'axios';
import { useAuth } from '@/contexts/AuthContext';
import { 
  GoogleMap, 
  DrawingManager,
  Polygon
} from '@react-google-maps/api';
import { useGoogleMapsApi, libraries } from '@/contexts/GoogleMapsContext';

const containerStyle = {
  width: '100%',
  height: '500px'
};

const center = {
  lat: 35.6895,
  lng: 139.6917
};

const polygonOptions = {
  fillColor: '#4CAF50',
  fillOpacity: 0.3,
  strokeColor: '#4CAF50',
  strokeOpacity: 1,
  strokeWeight: 2,
  clickable: true,
  editable: true,
  draggable: false,
  zIndex: 1
};

const NewFieldPage = () => {
  const [name, setName] = useState('');
  const [notes, setNotes] = useState('');
  const [coordinates, setCoordinates] = useState([]);
  const [area, setArea] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [mapLoaded, setMapLoaded] = useState(false);
  const [polygon, setPolygon] = useState(null);
  const [address, setAddress] = useState('');
  const [mapLoadError, setMapLoadError] = useState(null);
  
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  const mapRef = useRef(null);
  const geocoderRef = useRef(null);

  // Google Maps APIのロード状態を管理
  const { isLoaded, loadError } = useGoogleMapsApi();

  // マップロードエラー処理
  useEffect(() => {
    if (loadError) {
      console.error('Google Maps API load error:', loadError);
      setMapLoadError('Google Maps APIの読み込みに失敗しました。ページを再読み込みしてください。');
    }
  }, [loadError]);

  // マップのロード完了時の処理
  const onMapLoad = useCallback((map) => {
    mapRef.current = map;
    try {
      geocoderRef.current = new window.google.maps.Geocoder();
      setMapLoaded(true);
      console.log('Map loaded successfully');
    } catch (error) {
      console.error('Error initializing map components:', error);
      setMapLoadError('マップコンポーネントの初期化に失敗しました。');
    }
  }, []);

  // DrawingManagerのロード完了時の処理
  const onDrawingManagerLoad = useCallback((drawingManager) => {
    console.log('Drawing manager loaded');
    try {
      // 描画モードをポリゴンに設定
      if (window.google && window.google.maps && window.google.maps.drawing) {
        drawingManager.setDrawingMode(window.google.maps.drawing.OverlayType.POLYGON);
      }
    } catch (error) {
      console.error('Error setting drawing mode:', error);
    }
  }, []);

  // ポリゴン描画完了時の処理
  const onPolygonComplete = useCallback((poly) => {
    // 既存のポリゴンがあれば削除
    if (polygon) {
      polygon.setMap(null);
    }
    
    setPolygon(poly);
    
    // ポリゴンの座標を取得
    const path = poly.getPath();
    const coordsArray = [];
    
    for (let i = 0; i < path.getLength(); i++) {
      const point = path.getAt(i);
      coordsArray.push({
        lat: point.lat(),
        lng: point.lng()
      });
    }
    
    setCoordinates(coordsArray);
    
    // 面積を計算
    updatePolygonData(poly);
    
    // ポリゴンの編集イベントを監視
    window.google.maps.event.addListener(poly.getPath(), 'set_at', () => {
      updatePolygonData(poly);
    });
    
    window.google.maps.event.addListener(poly.getPath(), 'insert_at', () => {
      updatePolygonData(poly);
    });
    
    window.google.maps.event.addListener(poly.getPath(), 'remove_at', () => {
      updatePolygonData(poly);
    });
  }, [polygon]);

  // ポリゴンデータの更新処理
  const updatePolygonData = (poly) => {
    const path = poly.getPath();
    const coordsArray = [];
    
    for (let i = 0; i < path.getLength(); i++) {
      const point = path.getAt(i);
      coordsArray.push({
        lat: point.lat(),
        lng: point.lng()
      });
    }
    
    setCoordinates(coordsArray);
    
    try {
      // 面積計算（平方メートルからヘクタールに変換）
      if (window.google && window.google.maps && window.google.maps.geometry && window.google.maps.geometry.spherical) {
        const pathArray = path.getArray();
        const areaInSquareMeters = window.google.maps.geometry.spherical.computeArea(pathArray);
        const areaInHectares = areaInSquareMeters / 10000;
        setArea(parseFloat(areaInHectares.toFixed(4)));
        console.log(`Area calculated: ${areaInHectares.toFixed(4)} hectares`);
      } else {
        console.error('Google Maps Geometry library is not available');
        setError('面積計算に必要なライブラリが読み込まれていません');
      }
    } catch (err) {
      console.error('Error calculating area:', err);
      setError('面積計算中にエラーが発生しました');
    }
  };

  // 住所検索処理
  const handleAddressSearch = () => {
    if (!address || !geocoderRef.current) return;
    
    geocoderRef.current.geocode({ address }, (results, status) => {
      if (status === 'OK' && results[0]) {
        const location = results[0].geometry.location;
        mapRef.current.setCenter(location);
        mapRef.current.setZoom(18);
      } else {
        setError(`住所の検索に失敗しました: ${status}`);
      }
    });
  };

  // フォーム送信処理
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!name) {
      setError('圃場名は必須です');
      return;
    }
    
    if (coordinates.length < 3) {
      setError('有効なポリゴンを描画してください');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/fields`,
        {
          name,
          coordinates,
          area,
          notes: notes || null,
          address: address || null
        },
        {
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );
      
      setSuccess(true);
      setTimeout(() => {
        router.push('/fields');
      }, 2000);
    } catch (err) {
      console.error('Error creating field:', err);
      setError('圃場の作成中にエラーが発生しました');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <Box sx={{ p: 3 }}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h4" gutterBottom>
            新規圃場登録
          </Typography>
          
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          
          {success && (
            <Alert severity="success" sx={{ mb: 2 }}>
              圃場が正常に登録されました。リダイレクトします...
            </Alert>
          )}
          
          <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
            <TextField
              margin="normal"
              required
              fullWidth
              id="name"
              label="圃場名"
              name="name"
              autoComplete="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              autoFocus
            />
            
            <Box sx={{ mt: 3, mb: 2 }}>
              <Typography variant="h6" gutterBottom>
                住所検索
              </Typography>
              
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <TextField
                  fullWidth
                  id="address"
                  label="住所"
                  name="address"
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                  sx={{ mr: 1 }}
                />
                <Button 
                  onClick={handleAddressSearch}
                  disabled={!address || !mapLoaded}
                  variant="contained"
                >
                  検索
                </Button>
              </Box>
              
              {mapLoadError && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {mapLoadError}
                  <Button 
                    onClick={() => window.location.reload()} 
                    variant="outlined" 
                    size="small" 
                    sx={{ ml: 2 }}
                  >
                    ページを再読み込み
                  </Button>
                </Alert>
              )}
              
              {!isLoaded ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '500px' }}>
                  <CircularProgress />
                  <Typography variant="body1" sx={{ ml: 2 }}>
                    Google Maps を読み込み中...
                  </Typography>
                </Box>
              ) : (
                <Box sx={{ mb: 3, border: '1px solid #e0e0e0', borderRadius: 1 }}>
                  <GoogleMap
                    mapContainerStyle={containerStyle}
                    center={center}
                    zoom={16}
                    onLoad={onMapLoad}
                    options={{
                      mapTypeControl: true,
                      streetViewControl: true,
                      fullscreenControl: true,
                      zoomControl: true,
                      mapTypeId: 'roadmap',
                      mapTypeControlOptions: {
                        style: 2, // DROPDOWN_MENU
                        position: 3 // TOP_RIGHT
                      }
                    }}
                  >
                    {mapLoaded && (
                      <DrawingManager
                        onLoad={onDrawingManagerLoad}
                        onPolygonComplete={onPolygonComplete}
                        options={{
                          polygonOptions,
                          drawingControl: true,
                          drawingControlOptions: {
                            position: 1, // TOP_CENTER
                            // @ts-ignore - 型エラーを回避
                            drawingModes: ['polygon']
                          }
                        }}
                      />
                    )}
                    {coordinates.length > 0 && (
                      <Polygon
                        paths={coordinates}
                        options={polygonOptions}
                      />
                    )}
                  </GoogleMap>
                </Box>
              )}
              
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 2 }}>
                地図上で圃場の境界を描画してください。描画後も頂点をドラッグして編集できます。
              </Typography>
            </Box>
            
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2, p: 2, bgcolor: '#f5f5f5', borderRadius: 1 }}>
              <Typography variant="body1" sx={{ mr: 2 }}>
                圃場面積:
              </Typography>
              <Typography variant="h6" color="primary">
                {area.toFixed(2)} ha
              </Typography>
            </Box>
            
            <TextField
              margin="normal"
              fullWidth
              id="notes"
              label="備考"
              name="notes"
              multiline
              rows={4}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
            />
            
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
              <Button
                variant="outlined"
                onClick={() => router.push('/fields')}
                disabled={loading}
              >
                キャンセル
              </Button>
              
              <Button
                type="submit"
                variant="contained"
                disabled={loading || success || coordinates.length < 3}
              >
                {loading ? '登録中...' : '圃場を登録'}
              </Button>
            </Box>
          </Box>
        </Paper>
      </Box>
    </Layout>
  );
};

export default NewFieldPage;
