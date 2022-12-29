import { useFormikContext } from "formik";
import React from "react";
import { useWizard } from "react-use-wizard";
import image1 from "../../images/image1.png";
import image2 from "../../images/image2.png";
import image3 from "../../images/image3.png";
import image4 from "../../images/image4.png";
import image5 from "../../images/image5.png";
import Button from "../Button";

function Step5() {
  const { goToStep } = useWizard();
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
      </div>
    </>
  );
}

export default Step5;
