import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import Navbar from "./Navbar";

describe("Navbar コンポーネント", () => {
  // ログアウト関数のモック
  const mockOnLogout = vi.fn();

  beforeEach(() => {
    // 各テスト前にモック関数の呼び出し回数をリセット
    mockOnLogout.mockReset();
  });

  it("ナビゲーションバーが正しくレンダリングされる", () => {
    render(<Navbar onLogout={mockOnLogout} />);
    const title = screen.getByText(/My App/i);
    expect(title).toBeInTheDocument();
  });

  it("メニューボタンクリックでドロップダウンメニューが開く", async () => {
    render(<Navbar onLogout={mockOnLogout} />);
    const menuButton = screen.getByLabelText(/menu/i);
    fireEvent.click(menuButton);

    const profileMenuItem = await screen.findByText(/Profile/i);
    expect(profileMenuItem).toBeInTheDocument();
    const logoutMenuItem = await screen.findByText(/Logout/i);
    expect(logoutMenuItem).toBeInTheDocument();
  });

  it("「Logout」メニューアイテムクリックでログアウト処理が実行される", async () => {
    render(<Navbar onLogout={mockOnLogout} />);
    const menuButton = screen.getByLabelText(/menu/i);
    fireEvent.click(menuButton);

    const logoutMenuItem = await screen.findByText(/Logout/i);
    fireEvent.click(logoutMenuItem);

    expect(mockOnLogout).toHaveBeenCalledTimes(1);
  });
});
