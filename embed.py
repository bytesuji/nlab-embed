from InstructorEmbedding import INSTRUCTOR

class Embedder:
    def __init__(self, device='cuda', instruction=None):
        self.model = INSTRUCTOR('hkunlp/instructor-xl', device=device)
        print('initialized embedder on device', device)
        self.device = device
        self.instruction = instruction

    def embed(self, texts):
        if isinstance(texts, str):
            texts = [texts]
        if self.instruction:
            texts = [[self.instruction, t] for t in texts]
        # print('texts is', texts)
        return self.model.encode(texts).tolist()

    def run(self):
        pass
