import cv2

DUPLICATE_DESCRIPTOR_MATCHES_THRESHOLD = 50

class SiftDuplicateDetector:
    def __init__(self, images: dict):
        self._images = images
        self._computed_images = {}
        self._duplicates = {}
        
    def determine_duplicates(self):
        print('determine_duplicates using SIFT...')
        
        bfMatcher = cv2.BFMatcher(cv2.NORM_L1, crossCheck=True)
        self.compute_sift_keypoints_and_descriptors()
        
        for image in self._computed_images.keys():            
            print(f"\nFinding duplicates for {image}...")

            similar_images = self.find_similar_images(image, bfMatcher)

            if similar_images:
                self.store_duplicates(image, similar_images)  

        return self._duplicates
        
        
    def compute_sift_keypoints_and_descriptors(self):
        sift = cv2.xfeatures2d.SIFT_create()
        
        for path in self._images:
            image = cv2.imread(path)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)   
            image_keypoints, image_descriptors = sift.detectAndCompute(image, None)

            self._computed_images[path] = {
                'kp': image_keypoints, 
                'ds': image_descriptors, 
                'img': image
            }
            
    def find_similar_images(self, source_image: str, bfMatcher):
        similar_images = {}
        
        for image in self._computed_images.keys():
            if image == source_image: continue

            descriptor_matches = bfMatcher.match(self._computed_images[source_image]['ds'], self._computed_images[image]['ds'])

            # Discard if image is not similar enough                
            if (len(descriptor_matches) < DUPLICATE_DESCRIPTOR_MATCHES_THRESHOLD): continue

            similar_images[image] = {
                'num_matches': len(descriptor_matches), 
                'descriptor_matches': descriptor_matches
            }
            
        return similar_images
    
    def store_duplicates(self, source_image: str, similar_images):
        self._duplicates[source_image] = []

        # Sort by similarity; most similar ones first
        sorted_duplicates = sorted(similar_images.items(), key=lambda x:x[1]['num_matches'], reverse=True)
        
        for duplicate in sorted_duplicates:
            self._duplicates[source_image].append(duplicate[0])
        
        if (True):
            print("\tDuplicate(s) found:")
            
            for duplicate in sorted_duplicates:
                print(f"\t- {duplicate[0]}: Matched descriptors: {duplicate[1]['num_matches']}")             