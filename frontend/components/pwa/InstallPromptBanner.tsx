"use client";

import React, { useState, useEffect } from "react";
import { Download, Share, PlusSquare, X } from "lucide-react";
import { Button } from "../ui/Button";
import { useTranslation } from "../layout/DirectionProvider";

export const InstallPromptBanner: React.FC = () => {
  const { t } = useTranslation();
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null);
  const [showPrompt, setShowPrompt] = useState<boolean>(false);
  const [isIos, setIsIos] = useState<boolean>(false);
  const [isStandalone, setIsStandalone] = useState<boolean>(false);

  useEffect(() => {
    if (typeof window === "undefined") return;

    // Check if already in standalone mode
    const isStandaloneMode =
      window.matchMedia("(display-mode: standalone)").matches ||
      (window.navigator as any).standalone === true;

    setIsStandalone(isStandaloneMode);
    if (isStandaloneMode) return;

    // Check iOS Safari
    const userAgent = window.navigator.userAgent.toLowerCase();
    const isIosSafari =
      /iphone|ipad|ipod/.test(userAgent) &&
      /safari/.test(userAgent) &&
      !/crios|fxios/.test(userAgent);

    setIsIos(isIosSafari);

    // Check if dismissed in this session
    if (sessionStorage.getItem("coachos_pwa_prompt_dismissed")) {
      return;
    }

    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setShowPrompt(true);
    };

    window.addEventListener("beforeinstallprompt", handleBeforeInstallPrompt);

    if (isIosSafari) {
      setShowPrompt(true);
    }

    return () => {
      window.removeEventListener("beforeinstallprompt", handleBeforeInstallPrompt);
    };
  }, []);

  const handleInstallClick = async () => {
    if (!deferredPrompt) return;
    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    console.log("[PWA] User response to install prompt:", outcome);
    setDeferredPrompt(null);
    setShowPrompt(false);
  };

  const handleDismiss = () => {
    setShowPrompt(false);
    if (typeof window !== "undefined") {
      sessionStorage.setItem("coachos_pwa_prompt_dismissed", "true");
    }
  };

  if (!showPrompt || isStandalone) return null;

  return (
    <div
      role="region"
      aria-label="PWA Install Banner"
      className="bg-obsidian-900 border border-obsidian-800 rounded-xl p-4 my-4 shadow-lg text-brand-text flex flex-col md:flex-row items-start md:items-center justify-between gap-4"
    >
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 flex-shrink-0">
          <Download className="w-5 h-5" />
        </div>
        <div>
          <h3 className="text-sm font-semibold text-brand-text">{t("pwa.install_title")}</h3>
          <p className="text-xs text-brand-text-muted mt-0.5">{t("pwa.install_description")}</p>

          {isIos && (
            <div className="mt-2 text-xs bg-obsidian-800 p-2.5 rounded-lg border border-obsidian-700 space-y-1">
              <p className="font-medium text-emerald-400">{t("pwa.ios_instructions_title")}</p>
              <p className="flex items-center gap-1.5 text-brand-text-muted">
                <Share className="w-3.5 h-3.5 text-blue-400" />
                <span>{t("pwa.ios_instruction_step1")}</span>
              </p>
              <p className="flex items-center gap-1.5 text-brand-text-muted">
                <PlusSquare className="w-3.5 h-3.5 text-emerald-400" />
                <span>{t("pwa.ios_instruction_step2")}</span>
              </p>
            </div>
          )}
        </div>
      </div>

      <div className="flex items-center gap-2 self-end md:self-center">
        {!isIos && deferredPrompt && (
          <Button size="sm" variant="primary" onClick={handleInstallClick}>
            {t("pwa.install_button")}
          </Button>
        )}
        <Button size="sm" variant="ghost" onClick={handleDismiss}>
          <X className="w-4 h-4" />
        </Button>
      </div>
    </div>
  );
};
