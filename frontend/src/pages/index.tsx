import { useEffect } from 'react'
import { useRouter } from 'next/router'
import { Box, CircularProgress, Typography } from '@mui/material'

export default function Home() {
  const router = useRouter()

  useEffect(() => {
    // ルートページにアクセスした場合、圃場一覧ページにリダイレクト
    router.push('/fields')
  }, [router])

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        padding: 3,
      }}
    >
      <Typography variant="h4" component="h1" gutterBottom>
        SmartFarm Agent
      </Typography>
      <Typography variant="subtitle1" gutterBottom>
        リダイレクト中...
      </Typography>
      <CircularProgress sx={{ mt: 2 }} />
    </Box>
  )
}
