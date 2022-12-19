import { useFormikContext } from "formik";
import React from "react";

function Debug() {
  const ctx = useFormikContext();
  return (
    <div className="my-8 p-8 bg-red-50 overflow-x-scroll">
      <pre>{JSON.stringify(ctx, null, 2)}</pre>
    </div>
  );
}

export default Debug;
