import React, { useState } from 'react';
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  Button,
  VStack,
  Text,
  useToast,
  Box,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Input,
  FormControl,
  FormLabel,
  Textarea,
  useColorModeValue,
} from '@chakra-ui/react';
import { useAddWishlistItem } from '../hooks/useWishlistItems';

interface AddWishlistItemModalProps {
  isOpen: boolean;
  onClose: () => void;
  wishlistId: number;
}

export const AddWishlistItemModal: React.FC<AddWishlistItemModalProps> = ({
  isOpen,
  onClose,
  wishlistId,
}) => {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const toast = useToast();
  const { mutate: addWishlistItem } = useAddWishlistItem();

  // Manual form state
  const [title, setTitle] = useState('');
  const [price, setPrice] = useState('');
  const [description, setDescription] = useState('');
  const [imageUrl, setImageUrl] = useState('');

  const bgColor = useColorModeValue('white', 'gray.800');

  const handleAutoFill = async () => {
    if (!url) {
      toast({
        title: 'Please enter a URL',
        status: 'error',
        position: 'top',
        duration: 3000,
      });
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch('/api/wishlist-items/scrape_url/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch product data');
      }

      const data = await response.json();
      addWishlistItem({
        wishlist: wishlistId,
        url,
        ...data,
      });
      onClose();
      toast({
        title: 'Item added successfully',
        status: 'success',
        position: 'top',
        duration: 3000,
      });
    } catch (error) {
      toast({
        title: 'Error adding item',
        description: error instanceof Error ? error.message : 'Unknown error occurred',
        status: 'error',
        position: 'top',
        duration: 3000,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleManualAdd = () => {
    try {
      addWishlistItem({
        wishlist: wishlistId,
        url: url || null,
        title,
        price: price ? parseFloat(price) : null,
        description,
        image_url: imageUrl,
      });
      onClose();
      toast({
        title: 'Item added successfully',
        status: 'success',
        position: 'top',
        duration: 3000,
      });
    } catch (error) {
      toast({
        title: 'Error adding item',
        description: error instanceof Error ? error.message : 'Unknown error occurred',
        status: 'error',
        position: 'top',
        duration: 3000,
      });
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl">
      <ModalOverlay />
      <ModalContent bg={bgColor}>
        <ModalHeader>Add Wishlist Item</ModalHeader>
        <ModalCloseButton />
        <ModalBody pb={6}>
          <Tabs isFitted variant="enclosed">
            <TabList mb="1em">
              <Tab>Auto-fill from URL</Tab>
              <Tab>Manual Entry</Tab>
            </TabList>
            <TabPanels>
              <TabPanel>
                <VStack spacing={4}>
                  <Text>Enter a product URL to automatically fill the details</Text>
                  <Input
                    placeholder="https://example.com/product"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                  />
                  <Button
                    colorScheme="blue"
                    onClick={handleAutoFill}
                    isLoading={isLoading}
                    width="full"
                  >
                    Add Item
                  </Button>
                </VStack>
              </TabPanel>
              <TabPanel>
                <VStack spacing={4}>
                  <FormControl>
                    <FormLabel>Title</FormLabel>
                    <Input
                      value={title}
                      onChange={(e) => setTitle(e.target.value)}
                      placeholder="Product title"
                    />
                  </FormControl>
                  <FormControl>
                    <FormLabel>Price</FormLabel>
                    <Input
                      type="number"
                      value={price}
                      onChange={(e) => setPrice(e.target.value)}
                      placeholder="0.00"
                    />
                  </FormControl>
                  <FormControl>
                    <FormLabel>Description</FormLabel>
                    <Textarea
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      placeholder="Product description"
                    />
                  </FormControl>
                  <FormControl>
                    <FormLabel>Image URL</FormLabel>
                    <Input
                      value={imageUrl}
                      onChange={(e) => setImageUrl(e.target.value)}
                      placeholder="https://example.com/image.jpg"
                    />
                  </FormControl>
                  <FormControl>
                    <FormLabel>Product URL (optional)</FormLabel>
                    <Input
                      value={url}
                      onChange={(e) => setUrl(e.target.value)}
                      placeholder="https://example.com/product"
                    />
                  </FormControl>
                  <Button
                    colorScheme="blue"
                    onClick={handleManualAdd}
                    width="full"
                  >
                    Add Item
                  </Button>
                </VStack>
              </TabPanel>
            </TabPanels>
          </Tabs>
        </ModalBody>
      </ModalContent>
    </Modal>
  );
}; 