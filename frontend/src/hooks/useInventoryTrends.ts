import { useQuery } from "@tanstack/react-query";
import axios from "axios";

interface InventoryMetric {
  id: number;
  name: string;
  sku: string;
  currentStock: number;
  minStock: number;
  maxStock: number;
  changeAmount: number;
  changePercent: number | string;
}

export const useInventoryTrends = () => {
  return useQuery<InventoryMetric[]>({
    queryKey: ["inventoryMetrics"],
    queryFn: async () => {
      const res = await axios.get(
        `${import.meta.env.VITE_API_URL}/analytics/metrics`
      );
      return res.data;
    },
  });
};
