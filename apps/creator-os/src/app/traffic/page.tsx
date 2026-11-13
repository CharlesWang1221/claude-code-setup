import type { Metadata } from "next";
import TrafficView from "./traffic-view";

export const metadata: Metadata = {
  title: "總流量｜Creator OS",
  description: "《不標準答案》各平台成效總帳：集數 × 平台 × 觀察窗",
};

export default function TrafficPage() {
  return <TrafficView />;
}
