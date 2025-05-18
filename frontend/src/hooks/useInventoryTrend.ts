import { useQuery } from "@tanstack/react-query";
import axios from "axios";

interface InventoryTrendPoint {
  date: string;
  stock: number;
}

export const useInventoryTrend = () => {
  return useQuery<InventoryTrendPoint[]>({
    queryKey: ["inventoryTrend"],
    queryFn: async () => {
      const res = await axios.get(
        `${import.meta.env.VITE_API_URL}/analytics/inventory-trend`
      );
      return res.data;
    },
  });
};
