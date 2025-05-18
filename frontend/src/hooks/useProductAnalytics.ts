import { useQuery } from "@tanstack/react-query";
import axios from "axios";

interface ProductTrend {
  date: string;
  stock: number;
}

export function useProductAnalytics(productId: string, options?: { enabled?: boolean }) {
  return useQuery<ProductTrend[]>({
    queryKey: ["productAnalytics", productId],
    queryFn: async () => {
      const res = await axios.get(
        `${import.meta.env.VITE_API_URL}/analytics/product-trend/${productId}`
      );
      return res.data;
    },
    enabled: !!productId,
    ...options,
  });
}
