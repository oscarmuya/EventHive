import { REFRESH_TOKEN_URL } from "@/app/constants/urls";
import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";

const TOKEN_KEY = "EVENTHIVE:authToken";
const EXPIRY_KEY = "EVENTHIVE:authTokenExpiry";
const USER_KEY = "EVENTHIVE:authUser";

interface User {
  id?: number;
  email: string;
  username?: string;
  [key: string]: any; // for any extra fields from backend
}

interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  isExpired: boolean;
}

export function useAuthPersistor() {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [isExpired, setIsExpired] = useState(false);
  const router = useRouter();

  const refreshToken = () => {
    fetch(REFRESH_TOKEN_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    })
      .then((res) => {
        if (res.ok) {
          res.json().then((res) => {
            saveAuth(res.access, res.expires_in);
            setIsExpired(false);
          });
        } else {
          res.json().then((res) => {
            console.log(res);
            if (res.code === "refresh_token_not_found") {
              router.push("/login?next=" + window.location.href);
            }
          });
        }
      })
      .catch((err) => {
        console.log(err);
        if (err.code === "refresh_token_not_found") {
          router.push("/login?next=" + window.location.href);
        }
      });
  };

  // Timer to refresh token before it expires
  useEffect(() => {
    if (token && !isExpired) {
      const expiryTime = parseInt(localStorage.getItem(EXPIRY_KEY) || "0", 10);
      const timeUntilExpiry = expiryTime - Date.now() - 5;

      const timer = setTimeout(() => {
        refreshToken();
      }, timeUntilExpiry);

      return clearTimeout(timer);
    }
  }, []);

  useEffect(() => {
    const storedToken = localStorage.getItem(TOKEN_KEY);
    const storedExpiry = localStorage.getItem(EXPIRY_KEY);
    const storedUser = localStorage.getItem(USER_KEY);

    if (storedToken && storedExpiry) {
      const expiryTime = parseInt(storedExpiry, 10);

      if (Date.now() > expiryTime) {
        setIsExpired(true);
        refreshToken();
      } else {
        setToken(storedToken);
        setUser(storedUser ? JSON.parse(storedUser) : null);
        setIsExpired(false);
      }
    }
  }, []);

  // Save token + user
  const saveAuth = useCallback(
    (newToken: string, expirySeconds: number, userData?: User) => {
      const expiryTime = Date.now() + expirySeconds * 1000;

      localStorage.setItem(TOKEN_KEY, newToken);
      localStorage.setItem(EXPIRY_KEY, expiryTime.toString());
      if (userData) localStorage.setItem(USER_KEY, JSON.stringify(userData));

      setToken(newToken);
      if (userData) setUser(userData);
      setIsExpired(false);
    },
    []
  );

  // Clear all auth data
  const clearAuth = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(EXPIRY_KEY);
    localStorage.removeItem(USER_KEY);

    setToken(null);
    setUser(null);
    setIsExpired(true);
  }, []);

  const getToken = useCallback(() => token, [token]);
  const getUser = useCallback(() => user, [user]);

  return {
    token,
    user,
    isAuthenticated: !!token && !isExpired,
    isExpired,
    saveAuth,
    clearAuth,
    getToken,
    getUser,
  } as AuthState & {
    saveAuth: (token: string, expirySeconds: number, user: User) => void;
    clearAuth: () => void;
    getToken: () => string | null;
    getUser: () => User | null;
  };
}
