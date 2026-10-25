"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { api, setToken } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const auth = useMutation({
    mutationFn: () => (mode === "login" ? api.login(email, password) : api.register(email, password)),
    onSuccess: ({ access_token }) => {
      setToken(access_token);
      // make sure nothing cached from a previous user is shown
      queryClient.clear();
      router.replace("/");
    },
  });

  function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    auth.mutate();
  }

  return (
    <>
      <h1>BriefBase</h1>
      <h2>{mode === "login" ? "Log in" : "Create an account"}</h2>

      <form onSubmit={onSubmit}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder={mode === "register" ? "Password (min 8 characters)" : "Password"}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          minLength={mode === "register" ? 8 : undefined}
          required
        />
        {auth.error && <p className="error">{auth.error.message}</p>}
        <button type="submit" disabled={auth.isPending}>
          {mode === "login" ? "Log in" : "Register"}
        </button>
      </form>

      <p>
        {mode === "login" ? "No account yet? " : "Already registered? "}
        <button
          type="button"
          onClick={() => {
            setMode(mode === "login" ? "register" : "login");
            auth.reset();
          }}
        >
          {mode === "login" ? "Register" : "Log in"}
        </button>
      </p>
    </>
  );
}
