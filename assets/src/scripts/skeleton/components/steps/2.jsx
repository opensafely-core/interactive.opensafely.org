import React from "react";
import { useWizard } from "react-use-wizard";

function Step2() {
  const { previousStep, nextStep } = useWizard();

  return (
    <>
      {/* Report builder */}
      <button onClick={() => previousStep()} type="button">
        Previous ⏮️
      </button>
      <button onClick={() => nextStep()} type="button">
        Next ⏭
      </button>
    </>
  );
}

export default Step2;
