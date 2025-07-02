import { Routes, Route } from 'react-router-dom'
import HomePage from '@/pages/HomePage'
import UploadPage from '@/pages/UploadPage'
import ResultsPage from '@/pages/ResultsPage'
import AdminPage from '@/pages/AdminPage'
import { Layout } from '@/components/Layout'
import { ProcessingPage } from '@/components'
import ErrorBoundary from '@/components/ErrorBoundary'
import { ToastProvider } from '@/components/Toast'
import { ErrorProvider } from '@/contexts/ErrorContext'

function App() {
  return (
    <ErrorBoundary onError={(error, errorInfo) => {
      console.error('Global error boundary caught:', error, errorInfo);
    }}>
      <ToastProvider maxToasts={5}>
        <ErrorProvider maxRetries={3}>
          <Layout>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/upload" element={<UploadPage />} />
              <Route path="/processing/:taskId" element={<ProcessingPage />} />
              <Route path="/results/:jobId" element={<ResultsPage />} />
              <Route path="/admin" element={<AdminPage />} />
            </Routes>
          </Layout>
        </ErrorProvider>
      </ToastProvider>
    </ErrorBoundary>
  )
}

export default App