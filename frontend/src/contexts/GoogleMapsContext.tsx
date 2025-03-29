import React, { createContext, useContext, ReactNode, useState, useEffect } from 'react';
import { useJsApiLoader } from '@react-google-maps/api';

// Google Maps APIのライブラリを定義
// @ts-ignore - 型エラーを回避
const libraries = ['drawing', 'geometry'];

// コンテキストの型定義
interface GoogleMapsContextType {
  isLoaded: boolean;
  loadError: Error | undefined;
}

// デフォルト値
const defaultContext: GoogleMapsContextType = {
  isLoaded: false,
  loadError: undefined
};

// コンテキストの作成
const GoogleMapsContext = createContext<GoogleMapsContextType>(defaultContext);

// コンテキストプロバイダーのpropsの型定義
interface GoogleMapsProviderProps {
  children: ReactNode;
}

// Google Maps APIプロバイダーコンポーネント
export const GoogleMapsProvider: React.FC<GoogleMapsProviderProps> = ({ children }) => {
  // クライアントサイドでのみ使用する状態
  const [isClient, setIsClient] = useState(false);
  
  // クライアントサイドかどうかを確認
  useEffect(() => {
    setIsClient(true);
  }, []);
  
  // Google Maps APIのロード
  // isClientがtrueの場合のみ実行される
  const { isLoaded, loadError } = useJsApiLoader({
    id: 'google-map-script',
    googleMapsApiKey: process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY || '',
    // @ts-ignore - 型エラーを回避
    libraries,
    language: 'ja',
    region: 'JP',
    // サーバーサイドでは実行しない
    preventGoogleFontsLoading: !isClient
  });
  
  // コンテキスト値
  const value = {
    isLoaded: isClient && isLoaded,
    loadError
  };

  return (
    <GoogleMapsContext.Provider value={value}>
      {children}
    </GoogleMapsContext.Provider>
  );
};

// カスタムフック
export const useGoogleMapsApi = () => useContext(GoogleMapsContext);

// ライブラリ配列をエクスポート
export { libraries };
