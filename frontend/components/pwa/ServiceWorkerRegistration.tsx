"use client";

import { useEffect } from "react";
import { registerServiceWorker } from "@/lib/pwa/register-sw";

export const ServiceWorkerRegistration: React.FC = () => {
  useEffect(() => {
    registerServiceWorker();
  }, []);

  return null;
};
