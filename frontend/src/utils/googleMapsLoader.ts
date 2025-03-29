// Google Maps APIローダーの共通設定
// このファイルを使用することで、アプリケーション全体で一貫したGoogle Maps API設定を維持できます

import { useJsApiLoader } from '@react-google-maps/api';

// Google Maps APIの設定
const mapsApiOptions = {
  id: 'google-map-script',
  googleMapsApiKey: process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY || '',
  libraries: ['drawing', 'geometry'],
  language: 'ja',
  region: 'JP'
};

// Google Maps APIのロード設定
export const useGoogleMapsApi = () => {
  return useJsApiLoader(mapsApiOptions);
};

// 他のコンポーネントで使用するためのライブラリ配列
export const libraries = ['drawing', 'geometry'];
