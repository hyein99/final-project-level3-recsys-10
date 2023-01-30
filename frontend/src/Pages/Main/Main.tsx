import { useEffect, useRef, useState } from "react";
import type { FC } from "react";
import Map from "../Map/Map";

type userInfo = {
  gu: string;
};

const Main: FC<userInfo> = ({ gu }) => {
  const mapElement = useRef(null);
  const [houseInfo, setHouseInfo] = useState<HouseInfo>({
    houses: {},
  });

  type HouseInfo = {
    houses: object;
  };

  // Make the `request` function generic
  // to specify the return data type:
  function request<HouseInfo>(
    url: string,
    // `RequestInit` is a type for configuring
    // a `fetch` request. By default, an empty object.
    config: RequestInit = {}

    // This function is async, it will return a Promise:
  ): Promise<void | HouseInfo> {
    // Inside, we call the `fetch` function with
    // a URL and config given:
    return (
      fetch(url, config)
        // When got a response call a `json` method on it
        .then((response) => response.json())
        // and return the result data.
        .then((data) => setHouseInfo(data["houses"]))
    );
    // We also can use some post-response
    // data-transformations in the last `then` clause.
  }

  // Make the `request` function generic
  // to specify the return data type:
  async function request2<HouseInfo>(
    url: string,
    // `RequestInit` is a type for configuring
    // a `fetch` request. By default, an empty object.
    config: RequestInit = {}

    // This function is async, it will return a Promise:
  ): Promise<HouseInfo> {
    const response = await fetch(url, config);
    return await response.json();
  }

  useEffect(() => {
    request("http://27.96.130.120:30007/map/items", {
      method: "POST",
      mode: "cors",
      cache: "no-cache",
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
      },
      body: JSON.stringify({
        user_id: 1,
        user_gu: gu,
        house_ranking: {},
      }),
    });
  }, [gu]);

  //   if (Object.keys(houseInfo).length === 0) return <></>;
  return (
    <>
      <input
        style={{
          top: "2.2vw",
          left: "40.2vw",
          zIndex: "2",
          position: "absolute",
          border: "none",
        }}
      ></input>
      <Map houses={houseInfo} />
    </>
  );
};

export default Main;
