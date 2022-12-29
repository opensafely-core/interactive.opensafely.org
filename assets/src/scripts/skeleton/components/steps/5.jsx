import { useFormikContext } from "formik";
import React from "react";
import { useWizard } from "react-use-wizard";
import image1 from "../../images/image1.png";
import Button from "../Button";

function Step5() {
  const { previousStep } = useWizard();
  const { isSubmitting } = useFormikContext();

  return (
    <>
      <h1 className="text-4xl font-bold mb-4">Review and submit</h1>
      <img
        alt=""
        className="max-w-md my-2 p-2 border rounded overflow-hidden"
        src={image1}
      />
      <div className="flex flex-row w-full gap-2 mt-10">
        <Button disabled={isSubmitting} type="submit">
          Submit
        </Button>
        <Button onClick={() => previousStep()} variant="danger">
          Go back
        </Button>
      </div>
    </>
  );
}

export default Step5;
