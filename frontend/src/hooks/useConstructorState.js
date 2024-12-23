import { useState } from 'react';

export default function useConstructorState(itemTypes) {
  const [imageUrl, setImageUrl] = useState("https://static.tildacdn.com/tild6565-3136-4433-a563-386237633139/Iznanka___.jpg");
  const [selectedMenu, setSelectedMenu] = useState(1);
  const [selectedItem, setSelectedItem] = useState(0);
  const [selectedColors, setSelectedColors] = useState({
    product: "Красный",
    art_color: "gray-800",
  });
  const [selectedItemSize, setItemSize] = useState({
    item_size: "XS",
  });
  const [fadeClass, setFadeClass] = useState("opacity-100");
  const [selectedArt, setSelectedArt] = useState({
    is_art: "without-art"
  });

  const changeImage = (newImage) => {
    setFadeClass("fade-out");
    setTimeout(() => {
      setImageUrl(newImage);
      setFadeClass("");
    }, 250);
  };

  return {
    imageUrl,
    selectedMenu,
    selectedItem,
    selectedColors,
    selectedItemSize,
    fadeClass,
    selectedArt,
    setSelectedMenu,
    setSelectedItem,
    setSelectedColors,
    setItemSize,
    setSelectedArt,
    changeImage
  };
} 