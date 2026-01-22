/**
 * API Service for AI Data Assistant
 * Handles all communication with the backend with proper error handling
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

console.log('🔌 API URL:', API_BASE_URL);

/**
 * Upload a PDF file for ingestion
 */
export const uploadPDF = async (file) => {
  console.log('📤 Uploading PDF:', file.name);
  
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch(`${API_BASE_URL}/upload`, {
      method: 'POST',
      body: formData,
    });

    console.log('📊 Upload response status:', response.status);

    if (!response.ok) {
      const errorData = await response.json();
      console.error('❌ Upload error:', errorData);
      throw new Error(`Upload failed: ${errorData.detail || response.statusText}`);
    }

    const data = await response.json();
    console.log('✅ Upload successful:', data);
    
    return {
      success: true,
      chunks: data.chunks_created,
      message: data.message,
    };
  } catch (error) {
    console.error('❌ Upload error:', error.message);
    return {
      success: false,
      error: error.message,
    };
  }
};

/**
 * Ingest business data from MySQL
 */
export const ingestBusinessData = async () => {
  console.log('📥 Ingesting MySQL data');
  
  try {
    const response = await fetch(`${API_BASE_URL}/ingest/mysql`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    console.log('📊 Ingest response status:', response.status);

    if (!response.ok) {
      const errorData = await response.json();
      console.error('❌ Ingest error:', errorData);
      throw new Error(`Ingest failed: ${errorData.detail || response.statusText}`);
    }

    const data = await response.json();
    console.log('✅ Ingest successful:', data);
    
    return {
      success: true,
      rows: data.rows_ingested,
      status: data.status,
    };
  } catch (error) {
    console.error('❌ Ingest error:', error.message);
    return {
      success: false,
      error: error.message,
    };
  }
};

/**
 * Send a query to the assistant
 * Uses hybrid search (FAISS + BM25) + intelligent routing
 */
export const sendQuery = async (query) => {
  console.log('💬 Sending query:', query);
  
  try {
    const payload = { query };
    console.log('📤 Payload:', payload);

    const response = await fetch(`${API_BASE_URL}/ask`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    console.log('📊 Query response status:', response.status);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error('❌ Query error:', errorData);
      throw new Error(`Query failed: ${errorData.detail || response.statusText}`);
    }

    const data = await response.json();
    console.log('✅ Query response received:', data);
    
    // Handle answer - could be string or object
    let answerText = '';
    if (typeof data.answer === 'string') {
      answerText = data.answer;
    } else if (data.answer && typeof data.answer === 'object') {
      // If answer is object, try to get the 'result' field
      answerText = data.answer.result || data.answer.answer || JSON.stringify(data.answer);
    } else {
      answerText = String(data.answer || '');
    }
    
    console.log('   - mode:', data.mode);
    console.log('   - answer:', answerText.substring(0, 100) + '...');
    console.log('   - chart:', data.chart ? 'yes' : 'no');
    console.log('   - sources:', Array.isArray(data.sources) ? data.sources.length : 0);
    
    return {
      success: true,
      mode: data.mode || 'rag',
      answer: answerText,
      chart: data.chart || null,
      sources: Array.isArray(data.sources) ? data.sources : [],
    };
  } catch (error) {
    console.error('❌ Query error:', error.message);
    return {
      success: false,
      error: error.message,
      mode: 'rag',
      answer: '',
    };
  }
};

/**
 * Chat endpoint for RAG-only queries
 */
export const chat = async (question) => {
  console.log('💬 Chat query:', question);
  
  try {
    const response = await fetch(
      `${API_BASE_URL}/chat?question=${encodeURIComponent(question)}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    console.log('📊 Chat response status:', response.status);

    if (!response.ok) {
      const errorData = await response.json();
      console.error('❌ Chat error:', errorData);
      throw new Error(`Chat failed: ${errorData.detail || response.statusText}`);
    }

    const data = await response.json();
    console.log('✅ Chat response:', data);
    
    return {
      success: true,
      answer: data.answer,
    };
  } catch (error) {
    console.error('❌ Chat error:', error.message);
    return {
      success: false,
      error: error.message,
    };
  }
};

/**
 * Check API connectivity
 */
export const testConnection = async () => {
  console.log('🧪 Testing API connection...');
  
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (response.ok) {
      const data = await response.json();
      console.log('✅ API is reachable:', data);
      return { success: true, data };
    } else {
      console.error('❌ API returned error:', response.status);
      return { success: false, status: response.status };
    }
  } catch (error) {
    console.error('❌ Cannot reach API:', error.message);
    return { success: false, error: error.message };
  }
};