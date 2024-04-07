import { useState, useEffect } from "react";

const TOKEN_REFRESH_INTERVAL = 10 * 60 * 1000;

interface TokenResponse {
  id_token: string;
  access_token: string;
  refresh_token: string;
}

const getTokenFromAPI = async () => {
  const result = await fetch("/auth/token");
  if (result.status !== 200) {
    throw new Error("failed to fetch refreshed token")
  }
  const data = await result.json();
  return data as TokenResponse;
};

const refreshAccessToken = async () => {
  const result = await fetch("/auth/refresh");
  if (result.status === 304) {
    return null;
  }
  if (result.status !== 200) {
    throw new Error("failed to fetch refreshed token")
  }
  const data = await result.json();
  return data as TokenResponse;
};

const useAuth = () => {
  const [token, setToken] = useState<TokenResponse | null>(null);

  useEffect(() => {
    const fetchToken = async () => {
      // トークン取得のAPI呼び出し
      const token = await getTokenFromAPI();
      setToken(token);
    };

    if (!token) {
      fetchToken();
    }

    const intervalId = setInterval(async () => {
      // トークンのリフレッシュ処理
      const refreshedToken = await refreshAccessToken();
      if (refreshedToken !== null) {
        setToken(refreshedToken);
      }
    }, TOKEN_REFRESH_INTERVAL);

    return () => clearInterval(intervalId);
  }, [token]);

  return { token: (token && token.access_token) || null };
};
export default useAuth;
