import React from "react";
import { useWizard } from "react-use-wizard";
import image1 from "../../images/image1.png";
import image2 from "../../images/image2.png";
import image3 from "../../images/image3.png";
import image4 from "../../images/image4.png";
import image5 from "../../images/image5.png";
import Button from "../Button";

function Step3() {
  const { previousStep, nextStep } = useWizard();

  return (
    <>
      <h1 className="text-4xl font-bold mb-4">Preview your request</h1>
      <img
        alt=""
        className="max-w-md my-2 p-2 border rounded overflow-hidden"
        src={image1}
      />
      <img
        alt=""
        className="max-w-md my-2 p-2 border rounded overflow-hidden"
        src={image2}
      />
      <img
        alt=""
        className="max-w-md my-2 p-2 border rounded overflow-hidden"
        src={image3}
      />
      <img
        alt=""
        className="max-w-md my-2 p-2 border rounded overflow-hidden"
        src={image4}
      />
      <img
        alt=""
        className="max-w-md my-2 p-2 border rounded overflow-hidden"
        src={image5}
      />
      <div className="flex flex-row w-full gap-2 mt-10">
        <Button onClick={() => nextStep()}>Next</Button>
        <Button onClick={() => previousStep()} variant="danger">
          Go back
        </Button>
      </div>
    </>
  );
}

export default Step3;
