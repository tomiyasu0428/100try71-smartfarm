import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';
import axios from 'axios';
import { useRouter } from 'next/router';

interface User {
  id: string;
  name: string;
  email: string;
  organization_id: number;
  role: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: false,
  error: null,
  login: async () => {},
  logout: () => {},
  isAuthenticated: false,
});

export const useAuth = () => useContext(AuthContext);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  // ページロード時に認証状態を確認
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          // トークンを使用してユーザー情報を取得
          const response = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/auth/me`, {
            headers: {
              Authorization: `Bearer ${token}`
            }
          });
          setUser(response.data);
        } catch (err) {
          // トークンが無効な場合はログアウト
          localStorage.removeItem('token');
          setUser(null);
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, []);

  // ログイン処理
  const login = async (email: string, password: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/auth/login`, {
        username: email,
        password: password
      });
      
      const { access_token } = response.data;
      localStorage.setItem('token', access_token);
      
      // ユーザー情報を取得
      const userResponse = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/auth/me`, {
        headers: {
          Authorization: `Bearer ${access_token}`
        }
      });
      
      setUser(userResponse.data);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'ログインに失敗しました');
    } finally {
      setLoading(false);
    }
  };

  // ログアウト処理
  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    router.push('/login');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        error,
        login,
        logout,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
