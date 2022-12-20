import React from "react";
import { Wizard } from "react-use-wizard";
import { Step1, Step2, Step3 } from "./components/steps";
import useFormData from "./stores/form-data";

function App() {
  const formData = useFormData((state) => state);

  return (
    <>
      <Wizard>
        <Step1 />
        <Step2 />
        <Step3 />
      </Wizard>
      <div className="my-8 p-8 bg-red-50 overflow-x-scroll">
        <pre>{JSON.stringify(formData, null, 2)}</pre>
      </div>
    </>
  );
}

export default App;
