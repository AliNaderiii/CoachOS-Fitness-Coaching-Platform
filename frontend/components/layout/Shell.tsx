"use client";

import React from "react";
import { Header } from "./Header";
import { Footer } from "./Footer";
import { BottomNav } from "./BottomNav";
import { NetworkStatusBanner } from "../pwa/NetworkStatusBanner";
import { ServiceWorkerRegistration } from "../pwa/ServiceWorkerRegistration";

export interface ShellProps {
  children: React.ReactNode;
}

export const Shell: React.FC<ShellProps> = ({ children }) => {
  return (
    <div className="min-h-screen flex flex-col bg-obsidian-950 text-brand-text antialiased">
      <ServiceWorkerRegistration />
      <NetworkStatusBanner />
      <Header />
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {children}
      </main>
      <Footer />
      <BottomNav />
    </div>
  );
};
