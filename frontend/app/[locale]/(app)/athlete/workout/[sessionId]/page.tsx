"use client";

import React from "react";
import { useParams } from "next/navigation";
import { WorkoutSessionView } from "@/components/athlete/WorkoutSessionView";

export default function AthleteWorkoutPage() {
  const params = useParams<{ sessionId: string }>();
  const sessionId = params?.sessionId ?? "";
  return (
    <div className="py-4">
      <WorkoutSessionView sessionId={sessionId} />
    </div>
  );
}
