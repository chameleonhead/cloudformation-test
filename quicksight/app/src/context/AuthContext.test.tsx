import React from "react";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import { describe, it, expect, vi } from "vitest";
import { AuthProvider, useAuthContext } from "./AuthContext";

// useAuthContext を使用するテスト用のコンポーネント
const TestComponent: React.FC = () => {
  const { token } = useAuthContext();
  return <div>{token ? `Token: ${token}` : "No token"}</div>;
};

describe("AuthProvider と useAuthContext", () => {
  // useAuth フックのモック化
  vi.mock("../hooks/useAuth", () => {
    return {
      default: vi.fn(() => ({ token: "mock-token" })),
    };
  });

  it("子コンポーネントに認証状態（トークン）を提供する", () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );
    // 提供されたトークンを表示するか検証
    expect(screen.getByText("Token: mock-token")).toBeInTheDocument();
  });

  it("AuthProvider の外部で useAuthContext を使用するとエラーを投げる", () => {
    // エラーが投げられることを検証するためのテスト
    const renderOutsideProvider = () => render(<TestComponent />);
    expect(renderOutsideProvider).toThrowError(
      "useAuthContext must be used within an AuthProvider"
    );
  });
});
