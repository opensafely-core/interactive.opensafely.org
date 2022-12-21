import create from "zustand";
import { devtools } from "zustand/middleware";

const useFormData = create(
  devtools((set) => ({
    formData: {},
    addFormData: (data) =>
      set((state) => ({ formData: { ...state.formData, ...data } })),
    replaceFormData: (formData) => set(() => ({ formData })),
  }))
);

export default useFormData;
