import '@/styles/globals.css'
import type { AppProps } from 'next/app'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import { AuthProvider } from '@/contexts/AuthContext'
import { GoogleMapsProvider } from '@/contexts/GoogleMapsContext'

// テーマの設定
const theme = createTheme({
  palette: {
    primary: {
      main: '#4CAF50', // 農業をイメージした緑色
    },
    secondary: {
      main: '#FFC107', // 補助色として黄色
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: [
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
  },
})

export default function App({ Component, pageProps }: AppProps) {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <GoogleMapsProvider>
          <Component {...pageProps} />
        </GoogleMapsProvider>
      </AuthProvider>
    </ThemeProvider>
  )
}
