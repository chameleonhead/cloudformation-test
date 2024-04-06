import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

import type { UserConfig } from "vitest/config";

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./src/setupTests.ts"],
  },
} as UserConfig);
